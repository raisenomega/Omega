"""Video Production script writing and adaptation mixin"""
import logging
from app.infrastructure.ai._text_compat import generate_text
from app.services.video_pipeline import (
    VideoSpec,
    VideoScript,
    VideoScene,
    calculate_scene_count,
    validate_duration_for_platform,
    estimate_word_count,
)

logger = logging.getLogger(__name__)


class VideoProductionScriptMixin:
    """Script writing and platform adaptation methods"""

    async def write_video_script(
        self, spec: VideoSpec, brand_voice: str, key_message: str
    ) -> VideoScript:
        """Write complete video script with powerful hook"""
        hook_prompt = (
            f"Create a powerful 3-second video hook for:\n"
            f"Platform: {spec.platform}\n"
            f"Topic: {spec.title}\n"
            f"Audience: {spec.target_audience}\n"
            f"Style: {spec.style}\n\n"
            f"The hook must grab attention INSTANTLY. Return ONLY the hook text (15-20 words max)."
        )
        hook = await generate_text(agent_code="video_prompt_writer", prompt=hook_prompt, max_tokens=50, temperature=0.9)

        scene_count = calculate_scene_count(spec.duration_seconds)
        word_count = estimate_word_count(spec.duration_seconds)

        script_prompt = (
            f"Write a {spec.duration_seconds}-second video script for {spec.platform}.\n\n"
            f"Title: {spec.title}\n"
            f"Hook (already created): {hook.strip()}\n"
            f"Brand voice: {brand_voice}\n"
            f"Key message: {key_message}\n"
            f"Style: {spec.style} ({spec.visual_style})\n"
            f"Target: {spec.target_audience}\n\n"
            f"Create {scene_count} scenes with narration and visual descriptions.\n"
            f"End with a clear call-to-action.\n"
            f"Total words: ~{word_count}\n\n"
            f"Format each scene as:\n"
            f"SCENE X (Xs): [narration] | Visual: [description] | Overlay: [text or 'none'] | Transition: [cut/fade/slide]"
        )

        script_content = await generate_text(
            agent_code="video_prompt_writer", prompt=script_prompt, max_tokens=800, temperature=0.7
        )

        scenes = []
        scene_num = 1
        for line in script_content.split('\n'):
            if 'SCENE' in line.upper():
                scenes.append(VideoScene(
                    scene_number=scene_num,
                    duration_seconds=spec.duration_seconds // scene_count,
                    narration=line[:100],
                    visual_description=f"Visual for scene {scene_num}",
                    text_overlay=None,
                    transition="fade" if scene_num < scene_count else "cut",
                ))
                scene_num += 1

        if not scenes:
            scenes = [VideoScene(
                scene_number=1,
                duration_seconds=spec.duration_seconds,
                narration=key_message,
                visual_description=f"{spec.visual_style} visuals",
                text_overlay=spec.title,
                transition="fade",
            )]

        cta_prompt = f"Create a compelling call-to-action for a {spec.platform} video about: {spec.title}"
        cta = await generate_text(agent_code="video_prompt_writer", prompt=cta_prompt, max_tokens=30, temperature=0.8)

        return VideoScript(
            hook=hook.strip(),
            scenes=scenes,
            call_to_action=cta.strip(),
            total_duration_seconds=spec.duration_seconds,
            word_count=word_count,
        )

    async def adapt_script_for_platform(
        self, script: VideoScript, target_platform: str
    ) -> VideoScript:
        """Adapt existing script for another platform"""
        if not validate_duration_for_platform(target_platform, script.total_duration_seconds):
            script.total_duration_seconds = 60 if "shorts" in target_platform else 90

        prompt = (
            f"Adapt this video script for {target_platform}:\n\n"
            f"Original hook: {script.hook}\n"
            f"Original CTA: {script.call_to_action}\n"
            f"Duration: {script.total_duration_seconds}s\n\n"
            f"Maintain core message but optimize for {target_platform} audience."
        )

        await generate_text(agent_code="video_prompt_writer", prompt=prompt, max_tokens=400, temperature=0.7)

        adapted_scenes = [
            VideoScene(
                scene_number=scene.scene_number,
                duration_seconds=scene.duration_seconds,
                narration=scene.narration,
                visual_description=scene.visual_description,
                text_overlay=scene.text_overlay,
                transition=scene.transition,
            )
            for scene in script.scenes
        ]

        return VideoScript(
            hook=script.hook,
            scenes=adapted_scenes,
            call_to_action=script.call_to_action,
            total_duration_seconds=script.total_duration_seconds,
            word_count=script.word_count,
        )
