"""Lookup and normalization helpers for Content Lab text generation."""
from fastapi import HTTPException

CONTENT_TYPE_MAP = {
    "reel_script": "reel",
    "reel_tiktok": "reel",
    "ad": "anuncio",
    "hashtag": "hashtags",
    "topic": "hashtags",
}


def _lookup_client_and_account(supabase, account_id: str) -> tuple:
    """Lookup client data. Tries social_accounts first, then clients table."""
    account_response = supabase.client.table("social_accounts")\
        .select("client_id, platform, clients!inner(name, plan)")\
        .eq("id", account_id)\
        .execute()

    if account_response.data:
        account = account_response.data[0]
        return (
            account["client_id"],
            account["clients"]["name"],
            account["clients"].get("plan") or "pro_197",
            account["platform"],
            account_id
        )

    client_response = supabase.client.table("clients")\
        .select("id, name, plan")\
        .eq("id", account_id)\
        .execute()

    if not client_response.data:
        raise HTTPException(404, f"Account or client {account_id} not found")

    client = client_response.data[0]

    social_resp = supabase.client.table("social_accounts")\
        .select("id, platform")\
        .eq("client_id", client["id"])\
        .limit(1)\
        .execute()

    if not social_resp.data:
        raise HTTPException(400, f"Client {client['id']} has no social accounts")

    return (
        client["id"],
        client["name"],
        client.get("plan") or "pro_197",
        social_resp.data[0]["platform"],
        social_resp.data[0]["id"]
    )


def _normalize_plan(plan: str) -> str:
    """Normalize plan to match LLM_TIERS keys"""
    plan_map = {
        "basico": "basico_97",
        "pro": "pro_197",
        "enterprise": "enterprise_497",
        "basico_97": "basico_97",
        "pro_197": "pro_197",
        "enterprise_497": "enterprise_497"
    }
    return plan_map.get(plan, "pro_197")
