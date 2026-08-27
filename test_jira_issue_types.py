import os

import requests
from dotenv import load_dotenv


load_dotenv()


JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")


def get_issue_types():

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
        "/rest/api/3/issue/createmeta"
        f"?projectKeys={JIRA_PROJECT_KEY}"
        "&expand=projects.issuetypes"
    )

    response = requests.get(
        url,
        auth=(
            JIRA_EMAIL,
            JIRA_API_TOKEN
        ),
        headers={
            "Accept": "application/json"
        },
        timeout=10
    )

    print(
        f"HTTP status: {response.status_code}"
    )

    if response.status_code != 200:

        print(
            "Failed to retrieve issue types."
        )

        print(
            response.text
        )

        return

    data = response.json()

    projects = data.get(
        "projects",
        []
    )

    if not projects:

        print(
            "No project information returned."
        )

        return

    project = projects[0]

    print(
        f"\nProject: "
        f"{project.get('name')}"
    )

    print(
        f"Key: "
        f"{project.get('key')}"
    )

    print("\nAvailable issue types:")
    print("-" * 40)

    for issue_type in project.get(
        "issuetypes",
        []
    ):

        print(
            f"Name: {issue_type.get('name')}"
        )

        print(
            f"ID:   {issue_type.get('id')}"
        )

        print("-" * 40)


if __name__ == "__main__":
    get_issue_types()
