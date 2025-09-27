"""Shared data schemas for the agents."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ContextPack(BaseModel):
    issue_key: str
    summary: str
    risks: List[str] = Field(default_factory=list)
    acceptance: List[str] = Field(default_factory=list)
    links: List[str] = Field(default_factory=list)
    embeddings: List[float] = Field(default_factory=list)


class Review(BaseModel):
    repo: str
    pull_request: int
    findings: List[str] = Field(default_factory=list)
    suggested_changes: List[str] = Field(default_factory=list)
    status: str
    author: Optional[str] = None


class TestCase(BaseModel):
    id: str
    title: str
    steps: List[str] = Field(default_factory=list)
    expected: List[str] = Field(default_factory=list)


class TestRun(BaseModel):
    run_id: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    tool: str
    status: str
    artifacts: List[str] = Field(default_factory=list)
    links: List[str] = Field(default_factory=list)
    cases: List[TestCase] = Field(default_factory=list)
    traceability: Optional[dict] = None

