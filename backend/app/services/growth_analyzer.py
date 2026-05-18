"""
Growth Analyzer Service
Identifies growth opportunities and experiments
"""
from pydantic import BaseModel
from typing import List
import uuid


class GrowthOpportunity(BaseModel):
    """Growth opportunity definition"""
    opportunity_id: str
    opportunity_type: str  # "collaboration" | "trending_format" | "cross_platform" | "audience_gap" | "repurpose"
    title: str
    description: str
    potential_impact: str  # "low" | "medium" | "high" | "explosive"
    effort_required: str  # "low" | "medium" | "high"
    estimated_roi: float
    implementation_steps: List[str]
    time_to_results: str  # "days" | "weeks" | "months"
    platform: str


class GrowthExperiment(BaseModel):
    """Growth experiment design"""
    experiment_id: str
    hypothesis: str
    variable_tested: str  # "caption_length" | "posting_time" | "content_format" | "hashtag_count"
    control_description: str
    test_description: str
    success_metric: str
    target_improvement_percent: float
    duration_days: int
    status: str  # "planned" | "running" | "completed"


class GrowthReport(BaseModel):
    """Comprehensive growth analysis"""
    client_id: str
    current_growth_rate: float
    benchmark_growth_rate: float
    growth_gap: float
    top_opportunities: List[GrowthOpportunity]
    recommended_experiments: List[GrowthExperiment]
    quick_wins: List[str]
    estimated_potential: str  # "conservative" | "moderate" | "aggressive"


class GrowthAnalyzer:
    """Service for growth analysis"""

    @staticmethod
    def calculate_growth_gap(current: float, benchmark: float) -> float:
        """Calculate gap between current and benchmark growth"""
        return round(benchmark - current, 2)

    @staticmethod
    def rank_opportunities_by_roi(
        opportunities: List[GrowthOpportunity]
    ) -> List[GrowthOpportunity]:
        """Sort opportunities by ROI potential"""
        return sorted(
            opportunities,
            key=lambda x: x.estimated_roi,
            reverse=True
        )

    @staticmethod
    def estimate_experiment_duration(variable: str) -> int:
        """Estimate experiment duration in days"""
        durations = {
            "caption_length": 7,
            "posting_time": 14,
            "content_format": 21,
            "hashtag_count": 7,
            "default": 14
        }
        return durations.get(variable, durations["default"])

    @staticmethod
    def generate_opportunity_id() -> str:
        """Generate unique opportunity ID"""
        return f"opp_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def generate_experiment_id() -> str:
        """Generate unique experiment ID"""
        return f"exp_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def classify_impact(roi: float) -> str:
        """Classify impact level from ROI"""
        if roi >= 5.0:
            return "explosive"
        elif roi >= 3.0:
            return "high"
        elif roi >= 1.5:
            return "medium"
        else:
            return "low"

    @staticmethod
    def classify_effort(steps: int) -> str:
        """Classify effort required"""
        if steps <= 2:
            return "low"
        elif steps <= 4:
            return "medium"
        else:
            return "high"


# Global instance
growth_analyzer = GrowthAnalyzer()
