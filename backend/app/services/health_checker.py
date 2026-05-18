"""
Health Checker Service
System and agent health monitoring utilities
"""
from typing import Optional
from pydantic import BaseModel
import time
import logging

logger = logging.getLogger(__name__)


class ServiceHealth(BaseModel):
    """Health status of a service"""
    service_name: str
    status: str  # "healthy" | "degraded" | "down"
    response_time_ms: float
    last_checked: str
    error: Optional[str] = None


class SystemHealthReport(BaseModel):
    """Overall system health report"""
    overall_status: str  # "healthy" | "degraded" | "critical"
    services: list[ServiceHealth]
    agents_status: dict[str, str]
    error_rate_percent: float
    timestamp: str


class AgentPerformanceReport(BaseModel):
    """Agent performance metrics"""
    agent_id: str
    avg_response_time_ms: float
    success_rate: float
    requests_per_hour: int
    error_count: int
    status: str  # "healthy" | "slow" | "failing"


class SystemAnomaly(BaseModel):
    """Detected system anomaly"""
    anomaly_type: str  # "high_error_rate" | "slow_response" | "agent_down"
    severity: str  # "warning" | "critical"
    affected_component: str
    description: str
    detected_at: str


class AlertNotification(BaseModel):
    """Alert notification"""
    alert_id: str
    severity: str
    title: str
    message: str
    recommended_action: str
    timestamp: str


class HealthChecker:
    """Service for health checking and monitoring"""
    
    def __init__(self):
        self.health_thresholds = {
            "response_time_warning": 1000,  # ms
            "response_time_critical": 3000,  # ms
            "error_rate_warning": 5.0,  # percent
            "error_rate_critical": 15.0  # percent
        }
    
    def check_service_health(
        self,
        url: str,
        timeout: float = 2.0
    ) -> ServiceHealth:
        """
        Check health of a service endpoint
        
        Args:
            url: Service URL to check
            timeout: Request timeout in seconds
            
        Returns:
            ServiceHealth status
        """
        from datetime import datetime
        import httpx
        
        start_time = time.time()
        service_name = url.split('/')[-2] if '/' in url else url
        
        try:
            # Make actual HTTP request
            with httpx.Client(timeout=timeout) as client:
                response = client.get(url)
                response.raise_for_status()
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status based on response time
            if response_time < self.health_thresholds["response_time_warning"]:
                status = "healthy"
            elif response_time < self.health_thresholds["response_time_critical"]:
                status = "degraded"
            else:
                status = "down"
            
            return ServiceHealth(
                service_name=service_name,
                status=status,
                response_time_ms=round(response_time, 2),
                last_checked=datetime.now().isoformat(),
                error=None
            )
            
        except httpx.TimeoutException:
            return ServiceHealth(
                service_name=service_name,
                status="down",
                response_time_ms=timeout * 1000,
                last_checked=datetime.now().isoformat(),
                error="Request timeout"
            )
        except httpx.HTTPStatusError as e:
            return ServiceHealth(
                service_name=service_name,
                status="down",
                response_time_ms=(time.time() - start_time) * 1000,
                last_checked=datetime.now().isoformat(),
                error=f"HTTP {e.response.status_code}"
            )
        except Exception as e:
            return ServiceHealth(
                service_name=service_name,
                status="down",
                response_time_ms=(time.time() - start_time) * 1000,
                last_checked=datetime.now().isoformat(),
                error=str(e)
            )
    
    def calculate_error_rate(self, errors: int, total: int) -> float:
        """Calculate error rate percentage"""
        if total == 0:
            return 0.0
        
        rate = (errors / total) * 100
        return round(rate, 2)
    
    def classify_severity(
        self,
        error_rate: float,
        response_time: float
    ) -> str:
        """
        Classify severity based on metrics
        
        Returns: "healthy" | "warning" | "critical"
        """
        is_error_critical = error_rate >= self.health_thresholds["error_rate_critical"]
        is_error_warning = error_rate >= self.health_thresholds["error_rate_warning"]
        is_response_critical = response_time >= self.health_thresholds["response_time_critical"]
        is_response_warning = response_time >= self.health_thresholds["response_time_warning"]
        
        if is_error_critical or is_response_critical:
            return "critical"
        elif is_error_warning or is_response_warning:
            return "warning"
        else:
            return "healthy"
    
    def detect_anomaly(
        self,
        metric_name: str,
        current_value: float,
        historical_avg: float,
        threshold_multiplier: float = 2.0
    ) -> Optional[SystemAnomaly]:
        """
        Detect anomaly by comparing current value to historical average
        
        Args:
            metric_name: Name of the metric
            current_value: Current metric value
            historical_avg: Historical average
            threshold_multiplier: How many times above average is anomalous
            
        Returns:
            SystemAnomaly if detected, None otherwise
        """
        from datetime import datetime
        
        if historical_avg == 0:
            return None
        
        ratio = current_value / historical_avg
        
        if ratio >= threshold_multiplier:
            severity = "critical" if ratio >= 3.0 else "warning"
            
            return SystemAnomaly(
                anomaly_type="metric_spike",
                severity=severity,
                affected_component=metric_name,
                description=f"{metric_name} is {ratio:.1f}x higher than average",
                detected_at=datetime.now().isoformat()
            )
        
        return None
    
    def generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        import uuid
        return f"alert_{uuid.uuid4().hex[:8]}"


# Global instance
health_checker = HealthChecker()
