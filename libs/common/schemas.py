"""Shared Pydantic schemas mirroring Firestore collections."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ContextPack(BaseModel):
    id: str
    project_id: str
    repo: str
    pull_request: int
    summary: str = ""
    risks: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    related_links: List[str] = Field(default_factory=list)
    embeddings: List[float] = Field(default_factory=list)


class ReviewFinding(BaseModel):
    id: str
    file_path: str
    summary: str
    severity: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    recommendation: Optional[str] = None


class Review(BaseModel):
    id: str
    repo: str
    pull_request: int
    status: str
    created_at: datetime
    updated_at: datetime
    author: Optional[str] = None
    findings: List[ReviewFinding] = Field(default_factory=list)
    overall_comment: Optional[str] = None


class TestCase(BaseModel):
    id: str
    title: str
    steps: List[str] = Field(default_factory=list)
    expected_results: List[str] = Field(default_factory=list)
    status: str = "draft"


class TestRun(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    case_results: Dict[str, str] = Field(default_factory=dict)
    executed_by: Optional[str] = None

