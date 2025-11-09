from typing import List, Optional

import strawberry
from fastapi import Request
from strawberry.fastapi import GraphQLRouter

from app.config import settings
from app.domain.models import Memory as DomainMemory
from app.infra.repositories_pg import PgAgentRepo, PgMemoryRepo
from app.services.memory_service import MemoryService


@strawberry.type
class Memory:
    id: strawberry.ID
    agent_id: strawberry.ID
    kind: str
    content: str
    created_at: str


@strawberry.type
class Agent:
    id: strawberry.ID
    name: str
    description: Optional[str]

    @strawberry.field
    async def memories(self, info, kind: Optional[str] = None, limit: int = 20) -> List[Memory]:
        svc: MemoryService = info.context["svc"]
        _, mems = await svc.get_agent_with_memories(str(self.id), kind, limit)
        return [Memory(**m.__dict__) for m in mems]


@strawberry.type
class Query:
    @strawberry.field
    async def health(self) -> str:
        return "ok"

    @strawberry.field(description="Retorna o prompt do assistente do site.")
    async def assistantPrompt(self) -> str:
        return settings.assistant_prompt.strip()

    @strawberry.field
    async def agent(self, info, id: strawberry.ID) -> Optional[Agent]:
        svc: MemoryService = info.context["svc"]
        agent, _ = await svc.get_agent_with_memories(str(id), None, 1)
        return Agent(**agent.__dict__) if agent else None

    @strawberry.field
    async def searchMemories(
        self, info, agent_id: strawberry.ID, q: str, limit: int = 5
    ) -> List[Memory]:
        svc: MemoryService = info.context["svc"]
        mems = await svc.search(str(agent_id), q, limit)
        return [Memory(**m.__dict__) for m in mems]


@strawberry.input
class UpsertMemoryInput:
    id: Optional[strawberry.ID] = None
    agent_id: strawberry.ID
    kind: str
    content: str


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def upsertMemory(self, info, input: UpsertMemoryInput) -> Memory:
        svc: MemoryService = info.context["svc"]
        dom = DomainMemory(
            id=str(input.id) if input.id else "",
            agent_id=str(input.agent_id),
            kind=input.kind,
            content=input.content,
            created_at=None,
        )
        saved = await svc.upsert(dom)
        return Memory(**saved.__dict__)

    @strawberry.mutation
    async def deleteMemory(self, info, id: strawberry.ID) -> bool:
        svc: MemoryService = info.context["svc"]
        return await svc.delete(str(id))


schema = strawberry.Schema(query=Query, mutation=Mutation)


def get_router():
    agent_repo = PgAgentRepo()
    mem_repo = PgMemoryRepo()
    svc = MemoryService(agent_repo, mem_repo)

    async def context_getter(request: Request):
        api_key = settings.graphql_api_key
        if api_key:
            supplied = request.headers.get("x-api-key")
            if supplied != api_key:
                # Retorna contexto mínimo; Strawberry irá permitir execução mas podemos falhar em cada field se quiser.
                # Simplesmente levantamos exceção para bloquear.
                raise PermissionError("Invalid API key")
        return {"svc": svc, "ip": request.client.host}

    return GraphQLRouter(schema, context_getter=context_getter)
