from pydantic import BaseModel, Field, field_validator
from typing import Optional


class UserQuery(BaseModel):
    query: str = Field(..., min_length=3, max_length=300)

    @field_validator("query")
    @classmethod
    def must_be_music_related(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class QueryPlan(BaseModel):
    intent: str
    desired_mood: Optional[str] = None
    desired_genre: Optional[str] = None
    desired_energy: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    title: str
    artist: str
    genre: str
    mood: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    explanation: str


class AgentTrace(BaseModel):
    query: str
    plan: QueryPlan
    retrieved_count: int
    rag_context_used: list[str]
    recommendations: list[Recommendation]
    total_steps: int
    duration_seconds: float
