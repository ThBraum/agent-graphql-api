import uuid
from typing import Optional, List
from datetime import datetime
from app.domain.models import Agent, Memory
from app.domain.repositories import AgentRepository, MemoryRepository
from .db import get_pool


class PgAgentRepo(AgentRepository):
    async def get(self, agent_id: str) -> Optional[Agent]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id,name,description,created_at FROM agents WHERE id=$1", agent_id
            )
        return Agent(**dict(row)) if row else None

    async def list_memories(self, agent_id: str, kind: Optional[str], limit: int) -> List[Memory]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            if kind:
                rows = await conn.fetch(
                    """SELECT id,agent_id,kind,content,created_at
                       FROM memories WHERE agent_id=$1 AND kind=$2
                       ORDER BY created_at DESC LIMIT $3""",
                    agent_id,
                    kind,
                    limit,
                )
            else:
                rows = await conn.fetch(
                    """SELECT id,agent_id,kind,content,created_at
                       FROM memories WHERE agent_id=$1
                       ORDER BY created_at DESC LIMIT $2""",
                    agent_id,
                    limit,
                )
        return [Memory(**dict(r)) for r in rows]


class PgMemoryRepo(MemoryRepository):
    async def search(self, agent_id: str, q: str, limit: int) -> List[Memory]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT id,agent_id,kind,content,created_at
                   FROM memories
                   WHERE agent_id=$1 AND content ILIKE '%'||$2||'%'
                   ORDER BY created_at DESC LIMIT $3""",
                agent_id,
                q,
                limit,
            )
        return [Memory(**dict(r)) for r in rows]

    async def upsert(self, m: Memory) -> Memory:
        pool = await get_pool()
        mid = m.id or str(uuid.uuid4())
        async with pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO memories (id,agent_id,kind,content)
                   VALUES ($1,$2,$3,$4)
                   ON CONFLICT (id) DO UPDATE SET
                     agent_id=excluded.agent_id,
                     kind=excluded.kind,
                     content=excluded.content""",
                mid,
                m.agent_id,
                m.kind,
                m.content,
            )
            row = await conn.fetchrow(
                "SELECT id,agent_id,kind,content,created_at FROM memories WHERE id=$1", mid
            )
        return Memory(**dict(row))

    async def delete(self, memory_id: str) -> bool:
        pool = await get_pool()
        async with pool.acquire() as conn:
            res = await conn.execute("DELETE FROM memories WHERE id=$1", memory_id)
        return res.endswith("1")
