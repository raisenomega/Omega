"""
Context Service — Global knowledge base for all agents
Filosofía: No velocity, only precision 🐢💎
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

# Cache for global context (refresh every 5min)
_global_cache: Optional[str] = None
_global_cache_time: Optional[datetime] = None
CACHE_TTL_MINUTES = 5


class ContextService:
    """Service for managing context library documents"""

    def __init__(self):
        self.supabase = get_supabase_service()
        self.table = "context_library"

    async def get_global_context(self) -> str:
        """Get ALL context from library (global + client + department) with 1h caching."""
        global _global_cache, _global_cache_time
        now = datetime.utcnow()
        # Check cache validity
        if _global_cache and _global_cache_time:
            age_minutes = (now - _global_cache_time).total_seconds() / 60
            if age_minutes < CACHE_TTL_MINUTES:
                return _global_cache
        # Refresh from DB
        try:
            resp = self.supabase.client.table(self.table)\
                .select("name, content, scope, scope_id, tags")\
                .eq("is_active", True)\
                .order("scope")\
                .execute()
            if not resp.data:
                return ""

            docs = resp.data

            # Limit to 80K chars - prioritize global > client > department
            total_chars = sum(len(d['content']) for d in docs)
            if total_chars > 80000:
                docs.sort(key=lambda d: {'global': 0, 'client': 1, 'department': 2}.get(d['scope'], 3))
                selected = []
                chars = 0
                for doc in docs:
                    if chars + len(doc['content']) < 80000:
                        selected.append(doc)
                        chars += len(doc['content'])
                docs = selected

            # Build document index
            index_lines = []
            for doc in docs:
                scope_label = {
                    "global": "Global",
                    "client": f"Cliente: {doc.get('scope_id','')[:8]}..." if doc.get('scope_id') else "Cliente",
                    "department": f"Depto: {doc.get('scope_id','').upper()}" if doc.get('scope_id') else "Depto"
                }.get(doc['scope'], doc['scope'])

                index_lines.append(
                    f"  - [{scope_label}] {doc['name']} ({len(doc['content'])} chars)"
                )

            index_header = (
                f"\n\n=== DOCUMENTOS EN CONTEXT LIBRARY ({len(docs)} total) ===\n"
                + "\n".join(index_lines)
                + "\n\n=== CONTENIDO COMPLETO ===\n"
            )

            # Build context with scope labels
            context_parts = []
            for doc in docs:
                scope_label = {
                    "global": "📌 CONTEXTO GLOBAL",
                    "client": f"👤 CLIENTE: {doc.get('scope_id', 'N/A')}",
                    "department": f"🏢 DEPARTAMENTO: {doc.get('scope_id', 'N/A').upper() if doc.get('scope_id') else 'N/A'}"
                }.get(doc['scope'], doc['scope'].upper())

                context_parts.append(
                    f"\n\n=== {scope_label} — {doc['name']} ===\n{doc['content']}"
                )

            ctx = index_header + "\n".join(context_parts) if context_parts else ""
            _global_cache = ctx
            _global_cache_time = now
            logger.info(f"Context library refreshed: {len(docs)} docs ({len(ctx)} chars)")
            return ctx
        except Exception as e:
            logger.error(f"Failed to load context library: {e}")
            return ""

    async def get_context_for_agent(
        self, agent_code: str, client_id: Optional[str] = None, department: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all relevant context for an agent (global + client + department)."""
        try:
            conditions = [("scope", "eq", "global"), ("is_active", "eq", True)]
            # Query global
            global_docs = self.supabase.client.table(self.table)\
                .select("*")\
                .eq("scope", "global")\
                .eq("is_active", True)\
                .execute()
            # Query client if provided
            client_docs = []
            if client_id:
                client_resp = self.supabase.client.table(self.table)\
                    .select("*")\
                    .eq("scope", "client")\
                    .eq("scope_id", client_id)\
                    .eq("is_active", True)\
                    .execute()
                client_docs = client_resp.data or []
            # Query department if provided
            dept_docs = []
            if department:
                dept_resp = self.supabase.client.table(self.table)\
                    .select("*")\
                    .eq("scope", "department")\
                    .eq("scope_id", department)\
                    .eq("is_active", True)\
                    .execute()
                dept_docs = dept_resp.data or []
            # Combine all docs
            all_docs = (global_docs.data or []) + client_docs + dept_docs
            # Build concatenated context
            context = ""
            for doc in all_docs:
                context += f"\n--- {doc['name']} ({doc['scope']}) ---\n{doc['content']}\n"
            return {"context": context, "sources": [doc['name'] for doc in all_docs]}
        except Exception as e:
            logger.error(f"Failed to get context for agent {agent_code}: {e}")
            return {"context": "", "sources": []}
