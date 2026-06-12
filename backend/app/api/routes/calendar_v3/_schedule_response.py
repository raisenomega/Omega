"""Mapea rows insertadas -> ScheduledPostV3Response (extraído de schedule_post · C4 ≤75L)."""
from app.api.routes.calendar_v3.models.calendar_models import ScheduledPostV3Response


def to_responses(rows: list[dict], brand_voice_skipped: bool = False) -> list[ScheduledPostV3Response]:
    return [
        ScheduledPostV3Response(
            id=str(r["id"]),
            client_id=str(r["client_id"]),
            social_account_id=str(r.get("social_account_id") or "") or None,
            content_id=str(r.get("content_id") or "") or None,
            scheduled_for=str(r.get("scheduled_for") or ""),
            status=str(r.get("status") or "pending"),
            media_url=r.get("media_url"),
            brand_voice_skipped=brand_voice_skipped,
        )
        for r in rows
    ]
