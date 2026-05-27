"""GET /security-dev/health · verifica que las 4 keys están cargadas en Railway."""
import os
from typing import Optional, Dict, Any
from app.api.routes.auth.super_owner import require_super_owner


async def handle_dev_health(authorization: Optional[str]) -> Dict[str, Any]:
    await require_super_owner(authorization)
    return {
        "e2b_api_key":        bool(os.environ.get("E2B_API_KEY")),
        "railway_api_token":  bool(os.environ.get("RAILWAY_API_TOKEN")),
        "railway_project_id": bool(os.environ.get("RAILWAY_PROJECT_ID")),
        "github_token":       bool(os.environ.get("GITHUB_TOKEN")),
        "all_ready": all([
            bool(os.environ.get("E2B_API_KEY")),
            bool(os.environ.get("RAILWAY_API_TOKEN")),
            bool(os.environ.get("RAILWAY_PROJECT_ID")),
            bool(os.environ.get("GITHUB_TOKEN")),
        ]),
    }
