"""Video Production planning, hook optimization and idea generation mixin"""
from typing import List
import logging
from app.infrastructure.ai._text_compat import generate_text
from app.services.video_pipeline import VideoSpec, VideoScript, VideoProductionPlan

logger = logging.getLogger(__name__)


class VideoProductionContentMixin:
    """Production planning, hook optimization, and idea generation methods"""

    async def create_production_plan(
        self, spec: VideoSpec, script: VideoScript
    ) -> VideoProductionPlan:
        """Create detailed production plan with shot list"""
        prompt = (
            f"Create a production plan for this video:\n\n"
            f"Title: {spec.title}\n"
            f"Duration: {spec.duration_seconds}s\n"
            f"Platform: {spec.platform}\n"
            f"Scenes: {len(script.scenes)}\n\n"
            f"Provide:\n"
            f"1. Shot list (5-7 specific shots needed)\n"
            f"2. Text overlays (3-5 key text elements)\n"
            f"3. Audio suggestions (music style, sound effects)\n"
            f"4. Production tips (3-5 practical tips)"
        )

        await generate_text(agent_code="video_prompt_writer", prompt=prompt, max_tokens=600, temperature=0.6)

        shot_list = [
            f"Shot {i+1}: {spec.visual_style} angle"
            for i in range(min(6, len(script.scenes)))
        ]

        text_overlays = [
            {"text": script.hook, "timing": "0-3s"},
            {"text": script.call_to_action, "timing": f"{spec.duration_seconds-5}-{spec.duration_seconds}s"},
        ]

        audio_suggestions = [
            f"{spec.style} background music",
            "Upbeat tempo matching platform style",
            "Sound effects for transitions",
        ]

        production_tips = [
            f"Optimize for {spec.aspect_ratio} aspect ratio",
            "Shoot in good lighting for clarity",
            "Keep text large and readable on mobile",
        ]

        estimated_hours = (len(script.scenes) * 0.5) + 2.0

        return VideoProductionPlan(
            spec=spec,
            script=script,
            shot_list=shot_list,
            text_overlays=text_overlays,
            audio_suggestions=audio_suggestions,
            estimated_production_hours=estimated_hours,
            production_tips=production_tips,
        )

    async def optimize_hook(
        self, platform: str, niche: str, content_topic: str
    ) -> dict:
        """Generate 3 hook options for first 3 seconds"""
        prompt = (
            f"Create 3 different attention-grabbing hooks for a {platform} video.\n\n"
            f"Niche: {niche}\n"
            f"Topic: {content_topic}\n\n"
            f"Each hook must:\n"
            f"- Be 15-20 words max\n"
            f"- Create curiosity or urgency\n"
            f"- Work in first 3 seconds\n\n"
            f"Return as:\n"
            f"1. [hook]\n"
            f"2. [hook]\n"
            f"3. [hook]"
        )

        hooks_text = await generate_text(
            agent_code="video_prompt_writer", prompt=prompt, max_tokens=150, temperature=0.9
        )

        hooks = [
            line.strip()[3:].strip()
            for line in hooks_text.split('\n')
            if line.strip() and line[0].isdigit()
        ][:3]

        return {"hooks": hooks, "platform": platform, "niche": niche}

    async def generate_video_ideas(
        self, niche: str, platform: str, content_pillars: List[str]
    ) -> List[dict]:
        """Generate 5 video ideas with title, hook and concept"""
        prompt = (
            f"Generate 5 viral video ideas for {platform}.\n\n"
            f"Niche: {niche}\n"
            f"Content pillars: {', '.join(content_pillars)}\n\n"
            f"For each idea provide:\n"
            f"- Title (engaging, 5-10 words)\n"
            f"- Hook (first 3 seconds)\n"
            f"- Concept (brief description)\n\n"
            f"Format as:\n"
            f"1. TITLE | HOOK | CONCEPT"
        )

        ideas_text = await generate_text(
            agent_code="video_prompt_writer", prompt=prompt, max_tokens=500, temperature=0.8
        )

        ideas = []
        for line in ideas_text.split('\n'):
            if line.strip() and '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    title = parts[0].split('.', 1)[-1].strip()
                    ideas.append({"title": title, "hook": parts[1], "concept": parts[2]})

        return ideas[:5]
