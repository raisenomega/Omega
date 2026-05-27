"""
Monitor Agent
24/7 system monitoring and health checking
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.services.health_checker import (
    health_checker,
    SystemHealthReport,
    ServiceHealth,
    AgentPerformanceReport,
    SystemAnomaly,
    AlertNotification
)

logger = logging.getLogger(__name__)


class MonitorAgent(BaseAgent):
    """
    Agent specialized in system monitoring
    - Health checks of all agents
    - Performance monitoring
    - Anomaly detection
    - Alert generation
    """
    
    def __init__(self, agent_id: str = "monitor_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.MONITOR,
            model="claude-haiku-4-5-20251001",  # I2: lightweight tier para monitoreo
            tools=[
                "health_checker",
                "performance_tracker",
                "anomaly_detector",
                "alert_generator"
            ]
        )
        
        # Track agent endpoints
        self.agent_endpoints = {
            "content": "/api/v1/content/agent-status",
            "strategy": "/api/v1/strategy/agent-status",
            "analytics": "/api/v1/analytics/agent-status",
            "engagement": "/api/v1/engagement/agent-status"
        }
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute monitoring task"""
        self.set_state(AgentState.WORKING)
        
        try:
            task_type = task.get("type")
            
            if task_type == "system_health":
                result = await self.check_system_health()
            elif task_type == "agent_performance":
                result = await self.monitor_agent_performance(
                    task["agent_id"],
                    task.get("metrics", {})
                )
            elif task_type == "detect_anomalies":
                result = await self.detect_system_anomalies(
                    task.get("metrics_history", [])
                )
            elif task_type == "generate_alert":
                result = await self.generate_alert(task["anomaly"])
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            self.set_state(AgentState.IDLE)
            return result
            
        except Exception as e:
            logger.error(f"Monitor execution error: {e}")
            self.set_state(AgentState.ERROR)
            raise
    
    async def check_system_health(self) -> SystemHealthReport:
        """DEBT-050: estado REAL desde agent_executions (no hardcoded). Agentes sin
        corridas recientes (24h) → 'unknown' · NUNCA se inventa 'operational'/'healthy'."""
        import asyncio
        from datetime import datetime, timezone, timedelta
        from app.infrastructure.supabase_service import get_supabase_service

        now_iso = datetime.now(timezone.utc).isoformat()
        since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        try:
            sb = get_supabase_service()
            rows = (await asyncio.to_thread(
                lambda: sb.client.table("agent_executions")
                .select("agent_id, status, execution_time_ms")
                .gte("created_at", since).execute()
            )).data or []
        except Exception as e:
            logger.warning(f"check_system_health: agent_executions read failed: {e}")
            rows = []

        by_agent: Dict[str, Dict[str, Any]] = {}
        total = failed = 0
        for r in rows:
            aid = r.get("agent_id") or "unknown"
            a = by_agent.setdefault(aid, {"total": 0, "failed": 0, "ms": []})
            a["total"] += 1
            total += 1
            if r.get("status") == "failed":
                a["failed"] += 1
                failed += 1
            if r.get("execution_time_ms"):
                a["ms"].append(r["execution_time_ms"])

        services: List[ServiceHealth] = []
        agents_status: Dict[str, str] = {}
        for aid, a in by_agent.items():
            rate = health_checker.calculate_error_rate(a["failed"], a["total"])
            status = "down" if rate >= 50 else "degraded" if rate >= 15 else "healthy"
            avg_ms = round(sum(a["ms"]) / len(a["ms"]), 2) if a["ms"] else 0.0
            services.append(ServiceHealth(service_name=aid, status=status,
                            response_time_ms=avg_ms, last_checked=now_iso, error=None))
            agents_status[aid] = status

        error_rate = health_checker.calculate_error_rate(failed, total)
        overall = ("unknown" if total == 0
                   else "critical" if error_rate >= 15.0
                   else "degraded" if error_rate >= 5.0 else "healthy")
        return SystemHealthReport(
            overall_status=overall, services=services, agents_status=agents_status,
            error_rate_percent=error_rate, timestamp=now_iso,
        )
    
    async def monitor_agent_performance(
        self,
        agent_id: str,
        metrics: Dict[str, Any]
    ) -> AgentPerformanceReport:
        """Monitor individual agent performance"""
        # Extract metrics
        total_requests = metrics.get("total_requests", 100)
        successful_requests = metrics.get("successful_requests", 95)
        total_response_time = metrics.get("total_response_time_ms", 50000)
        error_count = metrics.get("error_count", 5)
        
        # Calculate performance metrics
        success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        avg_response_time = total_response_time / total_requests if total_requests > 0 else 0
        requests_per_hour = metrics.get("requests_per_hour", 10)
        
        # Determine status
        if success_rate < 90 or avg_response_time > 2000:
            status = "failing"
        elif success_rate < 95 or avg_response_time > 1000:
            status = "slow"
        else:
            status = "healthy"
        
        return AgentPerformanceReport(
            agent_id=agent_id,
            avg_response_time_ms=round(avg_response_time, 2),
            success_rate=round(success_rate, 2),
            requests_per_hour=requests_per_hour,
            error_count=error_count,
            status=status
        )
    
    async def detect_system_anomalies(
        self,
        metrics_history: List[Dict[str, Any]]
    ) -> List[SystemAnomaly]:
        """Detect anomalies in system metrics"""
        anomalies = []
        
        if not metrics_history:
            return anomalies
        
        # Analyze error rate trend
        recent_errors = [m.get("error_count", 0) for m in metrics_history[-10:]]
        if recent_errors:
            avg_errors = sum(recent_errors) / len(recent_errors)
            current_errors = recent_errors[-1]
            
            anomaly = health_checker.detect_anomaly(
                metric_name="error_rate",
                current_value=current_errors,
                historical_avg=avg_errors,
                threshold_multiplier=2.0
            )
            
            if anomaly:
                anomalies.append(anomaly)
        
        # Analyze response time trend
        recent_times = [m.get("response_time_ms", 0) for m in metrics_history[-10:]]
        if recent_times:
            avg_time = sum(recent_times) / len(recent_times)
            current_time = recent_times[-1]
            
            anomaly = health_checker.detect_anomaly(
                metric_name="response_time",
                current_value=current_time,
                historical_avg=avg_time,
                threshold_multiplier=1.5
            )
            
            if anomaly:
                anomalies.append(anomaly)
        
        return anomalies
    
    async def generate_alert(
        self,
        anomaly: SystemAnomaly
    ) -> AlertNotification:
        """Generate alert notification from anomaly"""
        alert_id = health_checker.generate_alert_id()
        
        # Generate title and message
        if anomaly.severity == "critical":
            title = f"🚨 CRITICAL: {anomaly.affected_component}"
            recommended_action = "Immediate investigation required"
        else:
            title = f"⚠️ WARNING: {anomaly.affected_component}"
            recommended_action = "Monitor closely, investigate if persists"
        
        message = f"{anomaly.description}. Type: {anomaly.anomaly_type}"
        
        return AlertNotification(
            alert_id=alert_id,
            severity=anomaly.severity,
            title=title,
            message=message,
            recommended_action=recommended_action,
            timestamp=datetime.now().isoformat()
        )


# Global instance
monitor_agent = MonitorAgent()
