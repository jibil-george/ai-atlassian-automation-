import os

from dotenv import load_dotenv
from google import genai

from app.models import JiraTicket


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not set"
    )


client = genai.Client(
    api_key=api_key
)


MODEL_NAME = "gemini-3.1-flash-lite"


def generate_ticket(
    requirement: str
) -> JiraTicket:

    prompt = f"""
You are an AI assistant that converts software requirements
into structured Jira tickets.

Your primary goal is to create a useful Jira ticket while
preserving the exact meaning of the original requirement.

============================================================
GROUNDING RULES
============================================================

1. Treat the original requirement as the only source of truth.

2. Do not invent requirements.

3. Do not add implementation details that are not specified.

4. Do not assume a particular UI element, button, API,
   database, validation mechanism, technology, workflow,
   error message, or system behavior unless it is explicitly
   stated or directly necessary to express the requirement.

5. Do not add additional business rules or constraints.

6. Do not add specific numbers, limits, time periods, or
   performance requirements unless they appear in the
   requirement.

7. A natural restatement of the requirement is allowed.

8. Acceptance criteria should describe WHAT must be true,
   not HOW the feature must be implemented.

9. If the requirement does not provide enough information
   for a detailed acceptance criterion, keep the criterion
   simple rather than inventing details.

============================================================
ISSUE TYPE DEFINITIONS
============================================================

Task:
Use Task when the requirement describes a specific piece of
work that needs to be completed without clearly describing
a user-facing capability.

Bug:
Use Bug when the requirement describes existing behavior that
is incorrect, broken, unexpected, or not working as intended.

Story:
Use Story when the requirement describes a new capability or
functionality that a user or administrator needs.

Improvement:
Use Improvement when an existing feature or process needs to
be enhanced or optimized.

============================================================
ISSUE TYPE RULES
============================================================

- Existing broken behavior → Bug
- New user-facing capability → Story
- Concrete implementation work without a clear user-facing
  capability → Task
- Enhancement of an existing capability → Improvement

============================================================
SUMMARY
============================================================

Create a concise, action-oriented summary.

The summary must not introduce new functionality.

============================================================
DESCRIPTION
============================================================

Write a short description that faithfully restates the
requirement.

Do not add technical implementation details.

============================================================
ACCEPTANCE CRITERIA
============================================================

Create clear, testable acceptance criteria.

Every acceptance criterion must be supported by the original
requirement.

Prefer fewer accurate criteria over many detailed criteria.

Do NOT invent:

- UI elements
- buttons
- input fields
- error messages
- validation rules
- database behavior
- API behavior
- permissions not stated
- technical implementation details
- unspecified business rules

============================================================
PRIORITY
============================================================

Choose a reasonable priority based on the requirement.

Do not invent a specific business deadline or severity level.

============================================================
LABELS
============================================================

Generate a small number of useful labels based on concepts
explicitly present in the requirement.

Do not create labels for technologies or systems that are not
mentioned.

============================================================
ORIGINAL REQUIREMENT
============================================================

{requirement}

============================================================

Return only the structured Jira ticket.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": JiraTicket,
        },
    )

    return JiraTicket.model_validate_json(
        response.text
    )