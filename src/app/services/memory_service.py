from typing import List, Optional

from app.domain.models import Memory
from app.domain.repositories import AgentRepository, MemoryRepository


class MemoryService:
    def __init__(self, agent_repo: AgentRepository, mem_repo: MemoryRepository):
        self.agent_repo = agent_repo
        self.mem_repo = mem_repo

    async def get_agent_with_memories(self, agent_id: str, kind: Optional[str], limit: int):
        agent = await self.agent_repo.get(agent_id)
        if not agent:
            return None, []
        mems = await self.agent_repo.list_memories(agent_id, kind, limit)
        return agent, mems

    async def search(self, agent_id: str, q: str, limit: int):
        return await self.mem_repo.search(agent_id, q, limit)

    async def upsert(self, m: Memory):
        return await self.mem_repo.upsert(m)

    async def delete(self, memory_id: str):
        return await self.mem_repo.delete(memory_id)
