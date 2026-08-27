from app.jira_service import create_jira_issue
from app.models import JiraTicket


def main():

    ticket = JiraTicket(
        summary="Test AI-generated Jira ticket",
        issue_type="Task",
        description=(
            "This is a test ticket created through "
            "the AI Atlassian Automation project."
        ),
        acceptance_criteria=[
            "The Jira issue is created successfully",
            "The issue contains the generated summary",
            "The issue contains the acceptance criteria",
        ],
        priority="Medium",
        labels=[
            "ai-automation",
            "test"
        ],
    )

    print("Creating Jira issue...")

    result = create_jira_issue(ticket)

    print("\nJira issue created successfully!")
    print(f"ID:  {result['id']}")
    print(f"Key: {result['key']}")
    print(f"URL: {result['url']}")


if __name__ == "__main__":
    main()