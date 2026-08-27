from google import genai

from app.models import GroundingEvaluation, JiraTicket


def evaluate_grounding(
    client: genai.Client,
    requirement: str,
    ticket: JiraTicket
) -> GroundingEvaluation:

    ticket_content = {
        "summary": ticket.summary,
        "description": ticket.description,
        "acceptance_criteria": ticket.acceptance_criteria,
    }

    prompt = f"""
You are evaluating the factual grounding of a generated Jira
ticket.

Your task is to determine whether the generated Jira ticket
introduces meaningful information that is not supported by the
original requirement.

============================================================
ORIGINAL REQUIREMENT
============================================================

{requirement}

============================================================
GENERATED TICKET CONTENT
============================================================

{ticket_content}

============================================================
WHAT TO EVALUATE
============================================================

Evaluate ONLY:

- summary
- description
- acceptance_criteria

Do NOT evaluate:

- issue_type
- priority
- labels

These are metadata fields and are allowed to be inferred.

============================================================
GROUNDING DEFINITION
============================================================

A statement is SUPPORTED if:

1. It is explicitly stated in the requirement.

OR

2. It is a natural restatement of the requirement.

OR

3. It is a necessary and direct implication of the requirement.

Examples of acceptable direct implications:

Requirement:
"The dashboard should display the user's five most recent
orders."

Criterion:
"The orders are visible on the dashboard."

This is SUPPORTED because displaying something necessarily
means it is visible.

Requirement:
"Users are sometimes logged out when navigating from the
dashboard to the profile page."

Criterion:
"The user remains logged in when navigating to the profile
page."

This is SUPPORTED because it directly describes the desired
correction to the reported problem.

============================================================
UNSUPPORTED INFORMATION
============================================================

A statement is UNSUPPORTED if it introduces a meaningful new
requirement or implementation detail.

Examples:

Requirement:
"Customers should be able to apply a discount code."

Criterion:
"An Apply button is displayed."

UNSUPPORTED because the requirement does not specify a button.

Requirement:
"Export user data as CSV."

Criterion:
"The CSV contains the user's email, name, address, and phone
number."

UNSUPPORTED because the requirement does not specify which
fields must be exported.

Requirement:
"Users can reset their password."

Criterion:
"The reset link expires after 15 minutes."

UNSUPPORTED because the requirement did not specify an expiry
period.

============================================================
IMPORTANT
============================================================

Do NOT mark something as unsupported merely because the wording
is different from the requirement.

Do NOT mark a necessary implication as unsupported.

Only report meaningful additions that could cause a developer
to implement behavior that was not actually requested.

If the generated ticket is fully supported, return:

grounded = true

and an empty unsupported_items list.

If unsupported information exists, return:

grounded = false

and list the unsupported statements.

Return only the requested structured output.
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": GroundingEvaluation,
        },
    )

    return GroundingEvaluation.model_validate_json(
        response.text
    )