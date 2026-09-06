from fastapi import FastAPI, HTTPException

from app.jira_service import create_jira_issue
from app.llm_service import generate_ticket
from app.models import (
    JiraTicket,
    TicketDraft,
    TicketGenerationRequest,
    TicketUpdateRequest,
)
from app.ticket_store import ticket_store


app = FastAPI(
    title="AI Atlassian Automation",
    description="AI-powered workflow automation for Jira and Confluence",
    version="0.2.0"
)


@app.get("/")
def root():
    return {
        "message": "AI Atlassian Automation API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post(
    "/tickets/process",
    response_model=TicketDraft
)
def process_ticket(
    request: TicketGenerationRequest
):
    """
    Process a natural-language requirement.

    Workflow:
    Requirement
        ->
    Gemini generates structured Jira ticket
        ->
    Create DRAFT
        ->
    Return draft for human review
    """

    try:
        ticket = generate_ticket(
            request.requirement
        )

        draft = ticket_store.create_draft(
            ticket
        )

        return draft

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@app.get(
    "/tickets/{draft_id}",
    response_model=TicketDraft
)
def get_ticket_draft(
    draft_id: str
):
    """
    Retrieve a ticket draft.
    """

    draft = ticket_store.get_draft(
        draft_id
    )

    if draft is None:
        raise HTTPException(
            status_code=404,
            detail="Draft not found"
        )

    return draft


@app.put(
    "/tickets/{draft_id}",
    response_model=TicketDraft
)
def update_ticket_draft(
    draft_id: str,
    updates: TicketUpdateRequest
):
    """
    Update an AI-generated draft before approval.
    """

    try:
        draft = ticket_store.update_draft(
            draft_id,
            updates
        )

        if draft is None:
            raise HTTPException(
                status_code=404,
                detail="Draft not found"
            )

        return draft

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@app.post(
    "/tickets/{draft_id}/approve",
    response_model=TicketDraft
)
def approve_ticket_draft(
    draft_id: str
):
    """
    Approve a draft.

    Workflow:
    DRAFT
        ->
    APPROVED
        ->
    Automatically create Jira issue
        ->
    CREATED
    """

    try:
        draft = ticket_store.approve_draft(
            draft_id
        )

        if draft is None:
            raise HTTPException(
                status_code=404,
                detail="Draft not found"
            )

        jira_result = create_jira_issue(
            draft.ticket
        )

        created_draft = ticket_store.mark_created(
            draft_id=draft_id,
            jira_key=jira_result["key"],
            jira_url=jira_result["url"]
        )

        return created_draft

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@app.post(
    "/tickets/{draft_id}/reject",
    response_model=TicketDraft
)
def reject_ticket_draft(
    draft_id: str
):
    """
    Reject a draft.

    No Jira ticket will be created.
    """

    try:
        draft = ticket_store.reject_draft(
            draft_id
        )

        if draft is None:
            raise HTTPException(
                status_code=404,
                detail="Draft not found"
            )

        return draft

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@app.post(
    "/tickets/create"
)
def create_ticket(
    ticket: JiraTicket
):
    """
    Legacy direct Jira creation endpoint.

    Kept temporarily for testing.
    The preferred workflow is:

    POST /tickets/process
    -> review
    -> approve
    """

    try:
        result = create_jira_issue(
            ticket
        )

        return {
            "status": "created",
            "ticket": ticket,
            "jira": result
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )