"""
Experiment Engine Service
Pure A/B testing and statistical analysis logic
"""
from pydantic import BaseModel
from typing import List
import uuid
import math


class ABVariant(BaseModel):
    """A/B test variant"""
    variant_id: str
    variant_name: str  # "A" | "B" | "C"
    description: str
    content: dict[str, str]  # The content being tested
    impressions: int
    engagements: int
    clicks: int
    conversions: int
    engagement_rate: float


class ABTestResult(BaseModel):
    """A/B test result with statistical analysis"""
    test_id: str
    winner_variant: str | None
    statistical_significance: float  # 0.0 to 1.0
    confidence_level: float  # 0.90 | 0.95 | 0.99
    is_conclusive: bool
    sample_size_per_variant: int
    minimum_sample_needed: int
    recommendation: str
    insights: List[str]


class Experiment(BaseModel):
    """Complete A/B test experiment"""
    experiment_id: str
    client_id: str
    hypothesis: str
    variable_tested: str  # "caption" | "image" | "posting_time" | "hashtags" | "cta" | "hook"
    variants: List[ABVariant]
    status: str  # "draft" | "running" | "completed" | "inconclusive"
    started_at: str
    completed_at: str | None
    target_sample_size: int
    platform: str


def calculate_engagement_rate(engagements: int, impressions: int) -> float:
    """
    Calculate engagement rate

    Args:
        engagements: Total engagements
        impressions: Total impressions

    Returns:
        Engagement rate (0.0 to 1.0)
    """
    if impressions == 0:
        return 0.0

    return engagements / impressions


def calculate_statistical_significance(
    control: ABVariant,
    test: ABVariant
) -> float:
    """
    Calculate statistical significance using Z-test for proportions
    Simplified implementation

    Args:
        control: Control variant
        test: Test variant

    Returns:
        P-value (0.0 to 1.0, lower = more significant)
    """
    # Calculate pooled proportion
    total_engagements = control.engagements + test.engagements
    total_impressions = control.impressions + test.impressions

    if total_impressions == 0:
        return 1.0  # No significance

    pooled_proportion = total_engagements / total_impressions

    # Calculate standard error
    se_control = math.sqrt(
        pooled_proportion * (1 - pooled_proportion) / max(control.impressions, 1)
    )
    se_test = math.sqrt(
        pooled_proportion * (1 - pooled_proportion) / max(test.impressions, 1)
    )

    se_diff = math.sqrt(se_control**2 + se_test**2)

    if se_diff == 0:
        return 1.0

    # Calculate Z-score
    z_score = abs(control.engagement_rate - test.engagement_rate) / se_diff

    # Convert to p-value (simplified)
    # For z > 1.96 (p < 0.05), z > 2.58 (p < 0.01)
    if z_score > 2.58:
        return 0.01
    elif z_score > 1.96:
        return 0.05
    elif z_score > 1.64:
        return 0.10
    else:
        return 1.0 - (z_score / 3.0)  # Approximate


def determine_minimum_sample_size(
    effect_size: float,
    confidence: float
) -> int:
    """
    Determine minimum sample size needed per variant
    Simplified formula

    Args:
        effect_size: Expected effect size (e.g., 0.1 for 10% improvement)
        confidence: Confidence level (0.90, 0.95, 0.99)

    Returns:
        Minimum sample size per variant
    """
    # Z-scores for confidence levels
    z_scores = {
        0.90: 1.64,
        0.95: 1.96,
        0.99: 2.58
    }

    z = z_scores.get(confidence, 1.96)

    # Assumed baseline rate
    baseline_rate = 0.05  # 5% engagement rate

    # Sample size formula (simplified)
    n = (2 * (z**2) * baseline_rate * (1 - baseline_rate)) / (effect_size**2)

    return max(100, int(n))  # Minimum 100 samples


def is_result_conclusive(
    significance: float,
    sample_size: int,
    minimum: int
) -> bool:
    """
    Determine if test result is conclusive

    Args:
        significance: Statistical significance (p-value)
        sample_size: Actual sample size
        minimum: Minimum required sample size

    Returns:
        True if result is conclusive
    """
    # Need sufficient sample size AND statistical significance
    has_sufficient_sample = sample_size >= minimum
    is_statistically_significant = significance < 0.05

    return has_sufficient_sample and is_statistically_significant


def generate_experiment_id() -> str:
    """Generate unique experiment ID"""
    return f"exp_{uuid.uuid4().hex[:12]}"


def generate_variant_id() -> str:
    """Generate unique variant ID"""
    return f"var_{uuid.uuid4().hex[:8]}"


def identify_winner(variants: List[ABVariant]) -> str | None:
    """
    Identify winning variant based on engagement rate

    Args:
        variants: List of variants

    Returns:
        Winner variant name or None
    """
    if not variants:
        return None

    winner = max(variants, key=lambda v: v.engagement_rate)

    # Check if winner is significantly better
    if winner.engagement_rate > 0 and winner.impressions >= 100:
        return winner.variant_name

    return None


def calculate_lift(control_rate: float, test_rate: float) -> float:
    """
    Calculate percentage lift

    Args:
        control_rate: Control engagement rate
        test_rate: Test engagement rate

    Returns:
        Lift percentage
    """
    if control_rate == 0:
        return 0.0

    return ((test_rate - control_rate) / control_rate) * 100
