"""Tests apply_logo_to_video (DEBT-FFMPEG) · FFmpeg subprocess + service-role logo download.

Best-effort: FFmpeg/ffprobe ausente o download fallo → retorna video_path original
(skip silencioso · nunca rompe el pipeline de generación). El logo se descarga vía
service-role (bucket privado · download_logo_bytes en _logo_overlay).
"""
import subprocess

import app.bc_cognition.infrastructure._logo_overlay_video as lov


def test_ffmpeg_missing_returns_original(monkeypatch):
    """Sin FFmpeg en PATH → skip · retorna video_path."""
    monkeypatch.setattr(lov.shutil, "which", lambda name: None)
    assert lov.apply_logo_to_video("/tmp/v.mp4", "http://x/logo.png") == "/tmp/v.mp4"


def test_ffprobe_missing_returns_original(monkeypatch):
    """Sin ffprobe (solo ffmpeg) → skip · retorna video_path."""
    monkeypatch.setattr(lov.shutil, "which",
                        lambda name: "/usr/bin/ffmpeg" if name == "ffmpeg" else None)
    assert lov.apply_logo_to_video("/tmp/v.mp4", "http://x/logo.png") == "/tmp/v.mp4"


def test_logo_download_fails_returns_original(monkeypatch):
    """download_logo_bytes retorna None (bucket privado fallo) → skip · retorna video_path."""
    monkeypatch.setattr(lov.shutil, "which", lambda name: "/usr/bin/" + name)
    monkeypatch.setattr(lov, "download_logo_bytes", lambda url: None)
    assert lov.apply_logo_to_video("/tmp/v.mp4", "http://x/logo.png") == "/tmp/v.mp4"


def test_ffmpeg_nonzero_returns_original(monkeypatch, tmp_path):
    """ffmpeg returncode != 0 → cleanup + retorna video_path original."""
    monkeypatch.setattr(lov.shutil, "which", lambda name: "/usr/bin/" + name)
    monkeypatch.setattr(lov, "download_logo_bytes", lambda url: b"png-bytes")

    def _run(cmd, **kwargs):
        if cmd[0] == "ffprobe":
            return subprocess.CompletedProcess(cmd, 0, stdout="1920\n", stderr="")
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr=b"encode err")

    monkeypatch.setattr(lov.subprocess, "run", _run)
    video_path = str(tmp_path / "v.mp4")
    open(video_path, "wb").write(b"video-bytes")
    assert lov.apply_logo_to_video(video_path, "http://x/logo.png") == video_path


def test_happy_path_returns_branded_with_correct_filter(monkeypatch, tmp_path):
    """ffprobe ok + ffmpeg ok → retorna path branded · filter_complex con 15%/80%/20px."""
    monkeypatch.setattr(lov.shutil, "which", lambda name: "/usr/bin/" + name)
    monkeypatch.setattr(lov, "download_logo_bytes", lambda url: b"png-bytes")

    captured: list = []

    def _run(cmd, **kwargs):
        captured.append(cmd)
        if cmd[0] == "ffprobe":
            return subprocess.CompletedProcess(cmd, 0, stdout="1920\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr=b"")

    monkeypatch.setattr(lov.subprocess, "run", _run)
    video_path = str(tmp_path / "v.mp4")
    open(video_path, "wb").write(b"video-bytes")
    out = lov.apply_logo_to_video(video_path, "http://x/logo.png")
    assert out != video_path  # branded path distinto
    ffmpeg_call = [c for c in captured if c[0] == "ffmpeg"][0]
    fc = ffmpeg_call[ffmpeg_call.index("-filter_complex") + 1]
    assert "scale=288:-1" in fc        # 1920 * 0.15 = 288
    assert "aa=0.8" in fc              # opacity 80%
    assert "overlay=W-w-20:H-h-20" in fc  # padding 20px inf-derecha
