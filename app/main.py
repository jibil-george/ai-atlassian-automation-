from fastapi import FastAPI, HTTPException

from app.llm_service import generate_ticket
from app.models import JiraTicket, TicketGenerationRequest
from app.jira_service import create_jira_issue


app = FastAPI(
    title="AI Atlassian Automation",
    description="AI-powered workflow automation for Jira and Confluence",
    version="0.1.0"
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


@app.post("/tickets/generate", response_model=JiraTicket)
def generate_jira_ticket(
    request: TicketGenerationRequest
):
    try:
        ticket = generate_ticket(
            request.requirement
        )

        return ticket

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@app.post("/tickets/create")
def create_ticket(
    ticket: JiraTicket
):
    try:
        result = create_jira_issue(ticket)

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