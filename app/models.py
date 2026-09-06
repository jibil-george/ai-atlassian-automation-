from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class JiraTicket(BaseModel):
    summary: str = Field(
        description="A short and clear title for the Jira ticket"
    )

    issue_type: Literal[
        "Task",
        "Bug",
        "Story",
        "Improvement"
    ]

    description: str = Field(
        description="A concise description based only on the requirement"
    )

    acceptance_criteria: list[str] = Field(
        description="Testable criteria directly supported by the requirement"
    )

    priority: Literal[
        "Low",
        "Medium",
        "High"
    ]

    labels: list[str]


class TicketGenerationRequest(BaseModel):
    requirement: str = Field(
        min_length=10,
        description="Software requirement to convert into a Jira ticket"
    )


class GroundingEvaluation(BaseModel):
    grounded: bool
    unsupported_items: list[str]


class DraftStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CREATED = "CREATED"


class TicketDraft(BaseModel):
    draft_id: str
    status: DraftStatus
    ticket: JiraTicket
    jira_key: str | None = None
    jira_url: str | None = None


class TicketUpdateRequest(BaseModel):
    summary: str | None = None

    issue_type: Literal[
        "Task",
        "Bug",
        "Story",
        "Improvement"
    ] | None = None

    description: str | None = None

    acceptance_criteria: list[str] | None = None

    priority: Literal[
        "Low",
        "Medium",
        "High"
    ] | None = None

    labels: list[str] | None = None
