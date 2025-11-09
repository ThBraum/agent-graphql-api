from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(slots=True)
class Agent:
    id: str
    name: str
    description: Optional[str]
    created_at: Optional[datetime] = None

@dataclass(slots=True)
class Memory:
    id: str
    agent_id: str
    kind: str
    content: str
    created_at: Optional[datetime] = None
