"""Handler: estado de rotación de secrets para el panel · owner-only · NUNCA expone el valor."""
from typing import Dict, Any, Optional

from app.api.routes.auth.auth_utils import require_superadmin
from app.workers.sentinel_secrets_monitor import compute_rotation_status


async def handle_secrets_rotation_status(authorization: Optional[str]) -> Dict[str, Any]:
    """Devuelve por cada secret: name, last_rotated_at, days_since, max_days, urgency, note."""
    await require_superadmin(authorization)
    return {"secrets": compute_rotation_status()}
