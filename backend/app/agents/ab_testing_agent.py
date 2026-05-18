"""
A/B Testing Agent
Specialized in scientific experimentation and statistical analysis
"""
from typing import Dict, Any, List
from datetime import datetime
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.infrastructure.ai.claude_service import claude_service
from app.services.experiment_engine import (
    Experiment,
    ABVariant,
    ABTestResult,
    generate_experiment_id,
    generate_variant_id,
    determine_minimum_sample_size,
)
from ._ab_testing_analysis_mixin import ABTestingAnalysisMixin

logger = logging.getLogger(__name__)


class ABTestingAgent(ABTestingAnalysisMixin, BaseAgent):
    """
    Agent specialized in A/B testing and experimentation
    - Scientific experiment design
    - Variant creation
    - Statistical analysis
    - Insight generation
    - Next test recommendations
    """

    def __init__(self, agent_id: str = "ab_testing_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.ANALYTICS,
            model="gpt-4",
            tools=["experiment_designer", "variant_generator", "statistical_analyzer", "insight_engine"],
        )
        self.experiments_db: Dict[str, Experiment] = {}

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute A/B testing task"""
        self.set_state(AgentState.WORKING)
        try:
            task_type = task.get("type")
            if task_type == "design_experiment":
                result = await self.design_experiment(
                    task["hypothesis"], task["variable"], task["base_content"], task["platform"]
                )
            elif task_type == "create_variants":
                result = await self.create_variants(
                    task["base_content"], task["variable"], task["client_niche"]
                )
            elif task_type == "analyze_results":
                result = await self.analyze_results(Experiment(**task["experiment"]))
            elif task_type == "generate_insights":
                result = await self.generate_insights(
                    [ABTestResult(**r) for r in task["results"]], task["client_id"]
                )
            elif task_type == "recommend_next":
                result = await self.recommend_next_test(
                    [Experiment(**e) for e in task["completed_experiments"]], task["client_goals"]
                )
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            self.set_state(AgentState.IDLE)
            return result.model_dump() if hasattr(result, 'model_dump') else result

        except Exception as e:
            logger.error(f"A/B testing execution error: {e}")
            self.set_state(AgentState.ERROR)
            raise

    async def design_experiment(
        self, hypothesis: str, variable: str, base_content: dict, platform: str
    ) -> Experiment:
        """Design scientific experiment with clear variants"""
        experiment_id = generate_experiment_id()

        prompt = (
            f"Design an A/B test experiment:\n\n"
            f"Hypothesis: {hypothesis}\n"
            f"Variable to test: {variable}\n"
            f"Platform: {platform}\n"
            f"Base content: {base_content}\n\n"
            f"Provide:\n"
            f"1. Clear hypothesis statement\n"
            f"2. Success metrics\n"
            f"3. Expected effect size"
        )

        await claude_service.generate_text(prompt=prompt, max_tokens=300, temperature=0.6)

        effect_size = 0.1
        confidence = 0.95
        min_sample = determine_minimum_sample_size(effect_size, confidence)

        experiment = Experiment(
            experiment_id=experiment_id,
            client_id="default_client",
            hypothesis=hypothesis,
            variable_tested=variable,
            variants=[],
            status="draft",
            started_at=datetime.now().isoformat(),
            completed_at=None,
            target_sample_size=min_sample,
            platform=platform,
        )

        self.experiments_db[experiment_id] = experiment
        logger.info(f"Designed experiment {experiment_id}")
        return experiment

    async def create_variants(
        self, base_content: dict, variable: str, client_niche: str
    ) -> List[ABVariant]:
        """Create A and B variants for testing"""
        prompt = (
            f"Create 2 variations for A/B testing:\n\n"
            f"Variable to test: {variable}\n"
            f"Niche: {client_niche}\n"
            f"Base content: {base_content}\n\n"
            f"Create:\n"
            f"Variant A (Control): {base_content.get('caption', 'Original version')}\n"
            f"Variant B (Test): Improved version focusing on {variable}\n\n"
            f"Make the change significant but focused on ONE variable only."
        )

        variants_text = await claude_service.generate_text(
            prompt=prompt, max_tokens=400, temperature=0.7
        )

        variant_a = ABVariant(
            variant_id=generate_variant_id(),
            variant_name="A",
            description="Control variant (original)",
            content=base_content,
            impressions=0,
            engagements=0,
            clicks=0,
            conversions=0,
            engagement_rate=0.0,
        )

        modified_content = base_content.copy()
        if variable == "caption":
            modified_content["caption"] = variants_text[:200]
        elif variable == "hashtags":
            modified_content["hashtags"] = ["#trending", "#viral", "#growth"]

        variant_b = ABVariant(
            variant_id=generate_variant_id(),
            variant_name="B",
            description=f"Test variant (modified {variable})",
            content=modified_content,
            impressions=0,
            engagements=0,
            clicks=0,
            conversions=0,
            engagement_rate=0.0,
        )

        return [variant_a, variant_b]


# Global instance
ab_testing_agent = ABTestingAgent()
