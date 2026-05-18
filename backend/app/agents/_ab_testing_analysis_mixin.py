"""A/B Testing analysis methods mixin: analyze, insights, recommendations"""
from typing import List
import logging
from app.infrastructure.ai.openai_service import openai_service
from app.services.experiment_engine import (
    ABVariant,
    ABTestResult,
    calculate_engagement_rate,
    calculate_statistical_significance,
    is_result_conclusive,
    identify_winner,
    calculate_lift,
)

logger = logging.getLogger(__name__)


class ABTestingAnalysisMixin:
    """Analysis methods for ABTestingAgent"""

    async def analyze_results(self, experiment) -> ABTestResult:
        """Analyze experiment results with statistical significance"""
        if len(experiment.variants) < 2:
            raise ValueError("Need at least 2 variants to analyze")

        for variant in experiment.variants:
            variant.engagement_rate = calculate_engagement_rate(
                variant.engagements, variant.impressions
            )

        control = experiment.variants[0]
        test = experiment.variants[1]

        significance = calculate_statistical_significance(control, test)
        winner = identify_winner(experiment.variants)
        avg_sample_size = sum(v.impressions for v in experiment.variants) // len(experiment.variants)
        conclusive = is_result_conclusive(
            significance, avg_sample_size, experiment.target_sample_size
        )
        lift = calculate_lift(control.engagement_rate, test.engagement_rate)

        prompt = (
            f"Analyze these A/B test results:\n\n"
            f"Variable tested: {experiment.variable_tested}\n"
            f"Control (A): {control.engagement_rate:.2%} engagement rate\n"
            f"Test (B): {test.engagement_rate:.2%} engagement rate\n"
            f"Lift: {lift:.1f}%\n"
            f"Statistical significance: p={significance:.3f}\n"
            f"Sample size: {avg_sample_size}\n\n"
            f"Provide 3 key insights about these results."
        )

        insights_text = await openai_service.generate_text(
            prompt=prompt, max_tokens=250, temperature=0.6
        )

        insights = [
            line.strip()
            for line in insights_text.split('\n')
            if line.strip() and len(line.strip()) > 15
        ][:3]

        if conclusive and winner:
            recommendation = f"Implement Variant {winner} - statistically significant improvement of {lift:.1f}%"
        elif not conclusive:
            recommendation = f"Continue test - need {experiment.target_sample_size - avg_sample_size} more samples"
        else:
            recommendation = "No significant difference - keep current approach"

        result = ABTestResult(
            test_id=experiment.experiment_id,
            winner_variant=winner,
            statistical_significance=significance,
            confidence_level=0.95,
            is_conclusive=conclusive,
            sample_size_per_variant=avg_sample_size,
            minimum_sample_needed=experiment.target_sample_size,
            recommendation=recommendation,
            insights=insights,
        )

        logger.info(f"Analyzed experiment {experiment.experiment_id}: winner={winner}")
        return result

    async def generate_insights(self, results: List[ABTestResult], client_id: str) -> List[str]:
        """Generate cumulative insights from multiple experiments"""
        prompt = f"Analyze these A/B test results for client {client_id}:\n\n"

        for i, result in enumerate(results[:5], 1):
            prompt += (
                f"{i}. Test {result.test_id}\n"
                f"   Winner: {result.winner_variant or 'None'}\n"
                f"   Conclusive: {result.is_conclusive}\n"
                f"   Insights: {', '.join(result.insights[:2])}\n\n"
            )

        prompt += (
            "Based on ALL these tests, provide 5 strategic insights:\n"
            "1. Patterns across tests\n"
            "2. What's working consistently\n"
            "3. What to avoid\n"
            "4. Audience preferences\n"
            "5. Next optimization opportunity"
        )

        insights_text = await openai_service.generate_text(
            prompt=prompt, max_tokens=400, temperature=0.6
        )

        return [
            line.strip()[3:].strip() if line.strip()[0].isdigit() else line.strip()
            for line in insights_text.split('\n')
            if line.strip() and len(line.strip()) > 20
        ][:5]

    async def recommend_next_test(
        self, completed_experiments: list, client_goals: List[str]
    ) -> dict:
        """Recommend next experiment based on history"""
        tested_variables = [exp.variable_tested for exp in completed_experiments]

        prompt = (
            f"Based on completed A/B tests, recommend the next experiment:\n\n"
            f"Already tested: {', '.join(tested_variables)}\n"
            f"Client goals: {', '.join(client_goals)}\n\n"
            f"Recommend:\n"
            f"1. Variable to test next\n"
            f"2. Hypothesis\n"
            f"3. Why this test matters\n"
            f"4. Expected impact"
        )

        recommendation_text = await openai_service.generate_text(
            prompt=prompt, max_tokens=300, temperature=0.7
        )

        untested_variables = ["cta", "hook", "image", "posting_time", "hashtags", "caption"]
        next_variable = next(
            (v for v in untested_variables if v not in tested_variables), "cta"
        )

        return {
            "recommended_variable": next_variable,
            "hypothesis": f"Testing {next_variable} will improve engagement",
            "reasoning": recommendation_text[:200],
            "expected_impact": "Moderate to high",
        }
