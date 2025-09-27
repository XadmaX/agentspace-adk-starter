"""Shared Pydantic schemas mirroring Firestore collections."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ContextPack(BaseModel):
    """Canonical representation of a generated context pack."""

    issue_key: str
    summary: str = ""
    risks: list[str] = Field(default_factory=list)
    acceptance: list[str] = Field(default_factory=list)
    related_links: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


class ReviewFinding(BaseModel):
    id: str
    file_path: str
    summary: str
    severity: str
    start_line: int | None = None
    end_line: int | None = None
    recommendation: str | None = None


class Review(BaseModel):
    id: str
    repo: str
    pull_request: int
    status: str
    created_at: datetime
    updated_at: datetime
    author: str | None = None
    findings: list[ReviewFinding] = Field(default_factory=list)
    overall_comment: str | None = None


class TestCase(BaseModel):
    id: str
    title: str
    steps: list[str] = Field(default_factory=list)
    expected_results: list[str] = Field(default_factory=list)
    status: str = "draft"


class TestRun(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime
    completed_at: datetime | None = None
    case_results: dict[str, str] = Field(default_factory=dict)
    executed_by: str | None = None
