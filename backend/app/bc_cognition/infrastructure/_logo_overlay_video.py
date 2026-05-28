"""Logo overlay para video vía FFmpeg subprocess (DEBT-FFMPEG · best-effort).

15% width · inf-derecha · 20px padding · 80% opac. Fail-graceful: si FFmpeg/ffprobe
ausente o cualquier paso falla → log + retorna video original. Nunca rompe el pipeline.
"""
import logging
import os
import shutil
import subprocess
import tempfile

import httpx

logger = logging.getLogger(__name__)
_LOGO_WIDTH_RATIO = 0.15
_PADDING = 20
_OPACITY = 0.80
_DL_TIMEOUT = 20.0
_FFMPEG_TIMEOUT = 180.0


def _silent_unlink(p: str) -> None:
    try:
        os.unlink(p)
    except OSError:
        pass


def apply_logo_to_video(video_path: str, logo_url: str) -> str:
    """Retorna path al video branded · si FFmpeg falla → retorna video_path original."""
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        logger.warning("logo overlay video skip · FFmpeg/ffprobe no en PATH")
        return video_path
    try:
        r = httpx.get(logo_url, timeout=_DL_TIMEOUT, follow_redirects=False)
        r.raise_for_status()
    except Exception as e:
        logger.warning(f"logo overlay video skip · download fallo: {e}")
        return video_path
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as lf:
        lf.write(r.content); logo_path = lf.name
    out_path = f"{video_path}.branded.mp4"
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width", "-of", "csv=p=0", video_path],
            capture_output=True, text=True, timeout=10,
        )
        logo_w = max(1, int(int(probe.stdout.strip()) * _LOGO_WIDTH_RATIO))
        cmd = ["ffmpeg", "-y", "-i", video_path, "-i", logo_path, "-filter_complex",
               f"[1:v]scale={logo_w}:-1,format=rgba,colorchannelmixer=aa={_OPACITY}[logo];"
               f"[0:v][logo]overlay=W-w-{_PADDING}:H-h-{_PADDING}",
               "-codec:a", "copy", out_path]
        result = subprocess.run(cmd, capture_output=True, timeout=_FFMPEG_TIMEOUT)
        if result.returncode != 0:
            logger.warning(f"logo overlay video fallo · ffmpeg rc={result.returncode}: "
                           f"{(result.stderr or b'')[:200]!r}")
            return video_path
    except Exception as e:
        logger.warning(f"logo overlay video error: {e}")
        return video_path
    finally:
        _silent_unlink(logo_path)
    return out_path


async def apply_logo_to_video_bytes(video_bytes: bytes, logo_url: str) -> bytes:
    """Bridging bytes ↔ tempfile · best-effort · bytes originales si no se aplica."""
    import asyncio
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tv:
        tv.write(video_bytes); tv_path = tv.name
    try:
        branded = await asyncio.to_thread(apply_logo_to_video, tv_path, logo_url)
        with open(branded, "rb") as f:
            out = f.read()
        if branded != tv_path:
            _silent_unlink(branded)
        return out
    finally:
        _silent_unlink(tv_path)
