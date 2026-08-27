import os

import requests
from dotenv import load_dotenv

from app.models import JiraTicket


load_dotenv()


JIRA_BASE_URL = os.getenv(
    "JIRA_BASE_URL",
    ""
).rstrip("/")

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")


def create_jira_issue(ticket: JiraTicket) -> dict:
    """
    Create a Jira issue from a structured JiraTicket.
    """

    if not JIRA_BASE_URL:
        raise RuntimeError(
            "JIRA_BASE_URL is not set in .env"
        )

    if not JIRA_EMAIL:
        raise RuntimeError(
            "JIRA_EMAIL is not set in .env"
        )

    if not JIRA_API_TOKEN:
        raise RuntimeError(
            "JIRA_API_TOKEN is not set in .env"
        )

    if not JIRA_PROJECT_KEY:
        raise RuntimeError(
            "JIRA_PROJECT_KEY is not set in .env"
        )

    url = (
        f"{JIRA_BASE_URL}"
        "/rest/api/3/issue"
    )

    acceptance_criteria = "\n".join(
        f"- {criterion}"
        for criterion in ticket.acceptance_criteria
    )

    description_text = (
        f"{ticket.description}\n\n"
        f"Acceptance Criteria:\n"
        f"{acceptance_criteria}"
    )

    payload = {
        "fields": {
            "project": {
                "key": JIRA_PROJECT_KEY
            },
            "summary": ticket.summary,
            "issuetype": {
                "name": ticket.issue_type
            },
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description_text
                            }
                        ]
                    }
                ]
            },
            "priority": {
                "name": ticket.priority
            },
            "labels": ticket.labels
        }
    }

    response = requests.post(
        url,
        auth=(
            JIRA_EMAIL,
            JIRA_API_TOKEN
        ),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=10
    )

    if response.status_code not in (200, 201):
        raise RuntimeError(
            "Jira issue creation failed: "
            f"{response.status_code} "
            f"{response.text}"
        )

    data = response.json()

    issue_key = data.get("key")

    return {
        "id": data.get("id"),
        "key": issue_key,
        "url": (
            f"{JIRA_BASE_URL}"
            f"/browse/{issue_key}"
        )
    }