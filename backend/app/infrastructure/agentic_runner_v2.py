# backend/app/infrastructure/agentic_runner_v2.py
# MAX 200 LINES — R-LINES-001
# AgenticRunnerV2 — AgenticRunner + Mem0 memoria persistente
# R-TENANT-001: user_id = client_id SIEMPRE
# R-ASYNC-001:  Mem0 calls síncronos → asyncio.to_thread()
# Estrategia: A/B paralelo. NO reemplaza v1 hasta métricas confirmadas.

from __future__ import annotations
import asyncio
import os
import time
from typing import Any

from langsmith import traceable
from mem0 import Memory

from app.infrastructure.agentic_runner import AgenticRunner, AgentResult

_MEM0_CONFIG = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": os.getenv("QDRANT_HOST", "localhost"),
            "port": int(os.getenv("QDRANT_PORT", 6333)),
            "collection_name": "omega_agent_memory",
        },
    },
    "llm": {
        "provider": "anthropic",
        "config": {
            "model": "claude-sonnet-4-20250514",
            "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
            "temperature": 0,
            "max_tokens": 2000,
        },
    },
    "embedder": {
        "provider": "anthropic",
        "config": {
            "model": "voyage-3",
            "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
        },
    },
}

_memory: Memory | None = None


def _get_memory() -> Memory:
    global _memory
    if _memory is None:
        _memory = Memory.from_config(_MEM0_CONFIG)
    return _memory


class AgenticRunnerV2(AgenticRunner):
    def __init__(self, agent_code: str, system_prompt: str, client_id: str | None = None):
        super().__init__(agent_code, system_prompt, client_id)
        self._mem = _get_memory()

    def _search_memories_sync(self, query: str) -> list[dict]:
        if not self.client_id:
            return []
        try:
            result = self._mem.search(
                query=query,
                user_id=self.client_id,
                limit=5,
                filters={"agent_code": self.agent_code},
            )
            return result.get("results", [])
        except Exception:
            return []

    def _add_memory_sync(self, task: str, content: str) -> None:
        if not self.client_id:
            return
        try:
            self._mem.add(
                messages=[
                    {"role": "user", "content": task},
                    {"role": "assistant", "content": content},
                ],
                user_id=self.client_id,
                metadata={"agent_code": self.agent_code},
            )
        except Exception:
            pass

    @traceable(run_type="chain")
    async def run(self, task: str) -> AgentResult:
        start = time.time()
        memories = await asyncio.to_thread(self._search_memories_sync, task)
        enriched_prompt = self.system_prompt
        if memories:
            memory_lines = "\n".join(f"- {m['memory']}" for m in memories)
            enriched_prompt = (
                f"{self.system_prompt}\n\n"
                f"MEMORIA DEL CLIENTE (interacciones anteriores):\n"
                f"{memory_lines}"
            )
        original_prompt = self.system_prompt
        self.system_prompt = enriched_prompt
        result: AgentResult = await super().run(task)
        self.system_prompt = original_prompt
        if result.success and result.content:
            await asyncio.to_thread(self._add_memory_sync, task, result.content)
        result.duration_ms = int((time.time() - start) * 1000)
        return result
