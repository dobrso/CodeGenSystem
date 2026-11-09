from typing import TypedDict, Literal

from pydantic import BaseModel, Field


class ArchitectFile(BaseModel):
    path: str
    purpose: str

class ArchitectInterface(BaseModel):
    name: str
    signature: str
    description: str

class ArchitectResponse(BaseModel):
    plan: list[str] = Field(default_factory=list)
    files: list[ArchitectFile] = Field(default_factory=list)
    interfaces: list[ArchitectInterface] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)

class DeveloperFileChange(BaseModel):
    path: str
    content: str

class DeveloperResponse(BaseModel):
    changes: list[DeveloperFileChange] = Field(default_factory=list)
    test_command: str
    notes: str
    escalation: list[str] = Field(default_factory=list)

class ReviewerIssue(BaseModel):
    file: str
    line: int
    description: str

class ReviewerCriteriaCheck(BaseModel):
    criterion: str
    satisfied: bool

class ReviewerResponse(BaseModel):
    verdict: Literal["APPROVE", "REJECT"]
    issues: list[ReviewerIssue] = Field(default_factory=list)
    criteria_checks: list[ReviewerCriteriaCheck] = Field(default_factory=list)

class AgentState(TypedDict, total=False):
    input: str
    recall_block: str
    architect_response: ArchitectResponse
    router_response: str
    developer_response: DeveloperResponse
    reviewer_response: ReviewerResponse
    output: str
    metrics: dict