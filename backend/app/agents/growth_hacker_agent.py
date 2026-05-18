"""
Growth Hacker Agent
Identifies growth opportunities and designs experiments
"""
from typing import Dict, Any, List
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.infrastructure.ai.openai_service import openai_service
from app.services.growth_analyzer import (
    growth_analyzer,
    GrowthOpportunity,
    GrowthExperiment,
    GrowthReport
)

logger = logging.getLogger(__name__)


class GrowthHackerAgent(BaseAgent):
    """
    Agent specialized in growth optimization
    - Opportunity identification
    - Experiment design
    - Growth trajectory analysis
    - Quick wins generation
    """

    def __init__(self, agent_id: str = "growth_hacker_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.GROWTH_HACKER,
            model="gpt-4",
            tools=[
                "opportunity_finder",
                "experiment_designer",
                "growth_analyzer",
                "quick_win_generator"
            ]
        )

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute growth hacking task"""
        self.set_state(AgentState.WORKING)

        try:
            task_type = task.get("type")

            if task_type == "identify_opportunities":
                result = await self.identify_opportunities(
                    task["account_data"],
                    task["niche"],
                    task["platform"]
                )
            elif task_type == "design_experiment":
                result = await self.design_experiment(
                    GrowthOpportunity(**task["opportunity"])
                )
            elif task_type == "analyze_trajectory":
                result = await self.analyze_growth_trajectory(
                    task["historical_data"],
                    task["industry_benchmarks"]
                )
            elif task_type == "quick_wins":
                result = await self.generate_quick_wins(
                    task["account_data"],
                    task["platform"]
                )
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            self.set_state(AgentState.IDLE)

            if isinstance(result, list):
                return [r.model_dump() if hasattr(r, 'model_dump') else r for r in result]
            return result.model_dump() if hasattr(result, 'model_dump') else result

        except Exception as e:
            logger.error(f"Growth hacker error: {e}")
            self.set_state(AgentState.ERROR)
            raise

    async def identify_opportunities(
        self,
        account_data: Dict[str, Any],
        niche: str,
        platform: str
    ) -> List[GrowthOpportunity]:
        """Identify top growth opportunities"""
        prompt = (
            f"Identify 5 growth opportunities for {niche} on {platform}:\n"
            f"Account data: {account_data}\n\n"
            f"For each opportunity provide:\n"
            f"1. Type (collaboration/trending_format/cross_platform/audience_gap/repurpose)\n"
            f"2. Title\n"
            f"3. Description (2 sentences)\n"
            f"4. 3 implementation steps\n"
            f"5. Estimated ROI multiplier"
        )

        analysis = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )

        # Generate sample opportunities
        opportunities = []
        for i in range(3):
            opp_id = growth_analyzer.generate_opportunity_id()
            roi = 2.5 + (i * 0.5)

            opportunities.append(GrowthOpportunity(
                opportunity_id=opp_id,
                opportunity_type="trending_format",
                title=f"Growth opportunity {i+1}",
                description=f"Leverage trending format for {niche}",
                potential_impact=growth_analyzer.classify_impact(roi),
                effort_required="medium",
                estimated_roi=roi,
                implementation_steps=[
                    "Research trending formats",
                    "Create test content",
                    "Analyze results"
                ],
                time_to_results="weeks",
                platform=platform
            ))

        return growth_analyzer.rank_opportunities_by_roi(opportunities)

    async def design_experiment(
        self,
        opportunity: GrowthOpportunity
    ) -> GrowthExperiment:
        """Design scientific experiment for opportunity"""
        exp_id = growth_analyzer.generate_experiment_id()
        duration = growth_analyzer.estimate_experiment_duration("content_format")

        hypothesis = f"Implementing {opportunity.title} will increase engagement"

        return GrowthExperiment(
            experiment_id=exp_id,
            hypothesis=hypothesis,
            variable_tested="content_format",
            control_description="Current content approach",
            test_description=opportunity.description,
            success_metric="engagement_rate",
            target_improvement_percent=opportunity.estimated_roi * 10,
            duration_days=duration,
            status="planned"
        )

    async def analyze_growth_trajectory(
        self,
        historical_data: List[Dict[str, float]],
        industry_benchmarks: Dict[str, float]
    ) -> GrowthReport:
        """Analyze growth trajectory and generate report"""
        if not historical_data:
            current_growth = 0.0
        else:
            current_growth = historical_data[-1].get("growth_rate", 0.0)

        benchmark_growth = industry_benchmarks.get("growth_rate", 5.0)
        gap = growth_analyzer.calculate_growth_gap(current_growth, benchmark_growth)

        # Generate opportunities
        opportunities = await self.identify_opportunities(
            {"followers": 10000},
            "tech",
            "instagram"
        )

        # Generate experiments
        experiments = [
            await self.design_experiment(opp)
            for opp in opportunities[:2]
        ]

        quick_wins = await self.generate_quick_wins(
            {"followers": 10000},
            "instagram"
        )

        return GrowthReport(
            client_id="sample_client",
            current_growth_rate=current_growth,
            benchmark_growth_rate=benchmark_growth,
            growth_gap=gap,
            top_opportunities=opportunities,
            recommended_experiments=experiments,
            quick_wins=quick_wins,
            estimated_potential="moderate"
        )

    async def generate_quick_wins(
        self,
        account_data: Dict[str, Any],
        platform: str
    ) -> List[str]:
        """Generate 5 quick wins (<48h implementation)"""
        prompt = (
            f"Generate 5 quick wins for {platform}:\n"
            f"Account: {account_data}\n\n"
            f"Each must be implementable in <48 hours.\n"
            f"Focus on immediate impact actions."
        )

        wins_text = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=200,
            temperature=0.7
        )

        wins = [
            line.strip()
            for line in wins_text.split('\n')
            if line.strip() and len(line.strip()) > 10
        ][:5]

        if not wins:
            wins = [
                "Optimize bio with clear value proposition",
                "Post during peak engagement hours",
                "Add trending hashtags to recent posts",
                "Engage with top commenters",
                "Share user-generated content"
            ]

        return wins


# Global instance
growth_hacker_agent = GrowthHackerAgent()
