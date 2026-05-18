"""
Report Builder Service
Builds executive reports and metrics summaries
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List


class ReportMetric(BaseModel):
    """Individual metric in report"""
    metric_name: str
    current_value: float
    previous_value: float
    change_percentage: float
    trend: str  # "up" | "down" | "stable"
    is_positive: bool


class ReportSection(BaseModel):
    """Section within report"""
    title: str
    summary: str
    metrics: List[ReportMetric]
    insights: List[str]
    recommendations: List[str]


class ExecutiveReport(BaseModel):
    """Complete executive report"""
    client_name: str
    report_type: str  # "monthly" | "weekly" | "quarterly" | "campaign"
    period_start: str
    period_end: str
    generated_at: str
    executive_summary: str
    overall_score: float  # 0.0 to 10.0
    key_wins: List[str]
    key_challenges: List[str]
    sections: List[ReportSection]
    next_period_goals: List[str]
    agency_notes: str


class ReportTemplate(BaseModel):
    """Report template definition"""
    template_id: str
    name: str
    required_sections: List[str]
    tone: str  # "formal" | "friendly" | "executive"


class ReportBuilder:
    """Service for building reports"""

    @staticmethod
    def calculate_change_percentage(
        current: float,
        previous: float
    ) -> float:
        """Calculate percentage change"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 2)

    @staticmethod
    def determine_trend(changes: List[float]) -> str:
        """Determine trend from change history"""
        if not changes:
            return "stable"

        avg_change = sum(changes) / len(changes)

        if avg_change > 5:
            return "up"
        elif avg_change < -5:
            return "down"
        else:
            return "stable"

    @staticmethod
    def calculate_overall_score(metrics: List[ReportMetric]) -> float:
        """Calculate overall performance score"""
        if not metrics:
            return 5.0

        positive_count = sum(1 for m in metrics if m.is_positive)
        score = (positive_count / len(metrics)) * 10

        return round(score, 1)

    @staticmethod
    def format_period_string(start: str, end: str) -> str:
        """Format period as readable string"""
        try:
            start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))

            return f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
        except:
            return f"{start} - {end}"

    @staticmethod
    def get_template(template_id: str) -> ReportTemplate:
        """Get report template by ID"""
        templates = {
            "monthly": ReportTemplate(
                template_id="monthly",
                name="Monthly Performance Report",
                required_sections=[
                    "Content Performance",
                    "Audience Growth",
                    "Engagement Metrics",
                    "Recommendations"
                ],
                tone="executive"
            ),
            "campaign": ReportTemplate(
                template_id="campaign",
                name="Campaign Results Report",
                required_sections=[
                    "Campaign Overview",
                    "Performance vs Goals",
                    "Key Learnings",
                    "Next Steps"
                ],
                tone="friendly"
            )
        }

        return templates.get(template_id, templates["monthly"])


# Global instance
report_builder = ReportBuilder()
