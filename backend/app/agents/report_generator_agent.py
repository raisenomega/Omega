"""
Report Generator Agent
Creates executive reports and summaries for clients
"""
from typing import Dict, Any, List
from datetime import datetime
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.infrastructure.ai.openai_service import openai_service
from app.services.report_builder import (
    report_builder,
    ExecutiveReport,
    ReportMetric,
    ReportSection
)

logger = logging.getLogger(__name__)


class ReportGeneratorAgent(BaseAgent):
    """
    Agent specialized in report generation
    - Monthly/weekly/quarterly reports
    - Campaign reports
    - Executive summaries
    - Markdown formatting
    """

    def __init__(self, agent_id: str = "report_generator_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.REPORT_GENERATOR,
            model="gpt-4",
            tools=[
                "report_builder",
                "metric_analyzer",
                "summary_writer",
                "markdown_formatter"
            ]
        )

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute report generation task"""
        self.set_state(AgentState.WORKING)

        try:
            task_type = task.get("type")

            if task_type == "generate_monthly":
                result = await self.generate_monthly_report(
                    task["client_name"],
                    task["metrics_data"],
                    task["previous_period_data"],
                    task.get("agency_notes", "")
                )
            elif task_type == "generate_campaign":
                result = await self.generate_campaign_report(
                    task["client_name"],
                    task["campaign_name"],
                    task["campaign_data"],
                    task["goals"]
                )
            elif task_type == "executive_summary":
                result = await self.write_executive_summary(
                    task["metrics"],
                    task["client_name"],
                    task["period"]
                )
            elif task_type == "format_markdown":
                result = await self.format_as_markdown(task["report"])
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            self.set_state(AgentState.IDLE)
            return result if isinstance(result, dict) else result.model_dump()

        except Exception as e:
            logger.error(f"Report generation error: {e}")
            self.set_state(AgentState.ERROR)
            raise

    async def generate_monthly_report(
        self,
        client_name: str,
        metrics_data: Dict[str, float],
        previous_period_data: Dict[str, float],
        agency_notes: str = ""
    ) -> ExecutiveReport:
        """Generate comprehensive monthly report"""
        # Build metrics
        metrics = []
        for key, current in metrics_data.items():
            previous = previous_period_data.get(key, 0)
            change = report_builder.calculate_change_percentage(current, previous)

            metrics.append(ReportMetric(
                metric_name=key,
                current_value=current,
                previous_value=previous,
                change_percentage=change,
                trend="up" if change > 0 else "down" if change < 0 else "stable",
                is_positive=change > 0
            ))

        # Generate executive summary
        summary = await self.write_executive_summary(
            metrics, client_name, "monthly"
        )

        # Identify wins and challenges
        wins = await self.identify_key_wins(metrics)
        challenges = self._identify_challenges(metrics)

        # Build sections
        sections = [
            ReportSection(
                title="Performance Overview",
                summary="Monthly performance analysis",
                metrics=metrics,
                insights=wins,
                recommendations=["Continue current strategy", "Focus on engagement"]
            )
        ]

        # Calculate overall score
        score = report_builder.calculate_overall_score(metrics)

        now = datetime.now().isoformat()

        return ExecutiveReport(
            client_name=client_name,
            report_type="monthly",
            period_start=now,
            period_end=now,
            generated_at=now,
            executive_summary=summary,
            overall_score=score,
            key_wins=wins,
            key_challenges=challenges,
            sections=sections,
            next_period_goals=["Increase engagement by 15%", "Launch new campaign"],
            agency_notes=agency_notes
        )

    async def generate_campaign_report(
        self,
        client_name: str,
        campaign_name: str,
        campaign_data: Dict[str, float],
        goals: Dict[str, float]
    ) -> ExecutiveReport:
        """Generate campaign performance report"""
        metrics = []
        for key, actual in campaign_data.items():
            goal = goals.get(key, 0)
            change = report_builder.calculate_change_percentage(actual, goal)

            metrics.append(ReportMetric(
                metric_name=key,
                current_value=actual,
                previous_value=goal,
                change_percentage=change,
                trend="up" if change > 0 else "down",
                is_positive=change > 0
            ))

        summary = await self.write_executive_summary(
            metrics, client_name, f"campaign: {campaign_name}"
        )

        wins = await self.identify_key_wins(metrics)

        now = datetime.now().isoformat()

        return ExecutiveReport(
            client_name=client_name,
            report_type="campaign",
            period_start=now,
            period_end=now,
            generated_at=now,
            executive_summary=summary,
            overall_score=report_builder.calculate_overall_score(metrics),
            key_wins=wins,
            key_challenges=[],
            sections=[],
            next_period_goals=[],
            agency_notes=""
        )

    async def write_executive_summary(
        self,
        metrics: List[ReportMetric],
        client_name: str,
        period: str
    ) -> str:
        """Write executive summary narrative"""
        metrics_summary = "\n".join([
            f"- {m.metric_name}: {m.current_value} "
            f"({'+' if m.change_percentage > 0 else ''}{m.change_percentage}%)"
            for m in metrics[:5]
        ])

        prompt = (
            f"Write a professional executive summary for {client_name}'s "
            f"{period} report.\n\n"
            f"Metrics:\n{metrics_summary}\n\n"
            f"Write 2-3 paragraphs summarizing performance, highlighting wins, "
            f"and providing strategic context. Tone: professional, data-driven."
        )

        summary = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=250,
            temperature=0.7
        )

        return summary.strip()

    async def identify_key_wins(
        self,
        metrics: List[ReportMetric]
    ) -> List[str]:
        """Identify top achievements"""
        positive_metrics = sorted(
            [m for m in metrics if m.is_positive],
            key=lambda x: x.change_percentage,
            reverse=True
        )

        wins = []
        for metric in positive_metrics[:3]:
            wins.append(
                f"{metric.metric_name} increased by {metric.change_percentage}%"
            )

        return wins

    def _identify_challenges(self, metrics: List[ReportMetric]) -> List[str]:
        """Identify areas needing improvement"""
        negative_metrics = sorted(
            [m for m in metrics if not m.is_positive],
            key=lambda x: x.change_percentage
        )

        challenges = []
        for metric in negative_metrics[:2]:
            challenges.append(
                f"{metric.metric_name} declined by {abs(metric.change_percentage)}%"
            )

        return challenges

    async def format_as_markdown(
        self,
        report: Dict[str, Any]
    ) -> str:
        """Format report as markdown"""
        md = f"# {report['client_name']} - {report['report_type'].title()} Report\n\n"
        md += f"**Period**: {report['period_start']} to {report['period_end']}\n\n"
        md += f"## Executive Summary\n\n{report['executive_summary']}\n\n"
        md += f"## Overall Score: {report['overall_score']}/10\n\n"

        if report.get('key_wins'):
            md += "## Key Wins\n\n"
            for win in report['key_wins']:
                md += f"- {win}\n"
            md += "\n"

        return md


# Global instance
report_generator_agent = ReportGeneratorAgent()
