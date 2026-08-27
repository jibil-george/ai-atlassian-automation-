import os

import requests
from dotenv import load_dotenv


load_dotenv()


JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")


def test_jira_connection():

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

    url = (
        f"{JIRA_BASE_URL}"
        "/rest/api/3/myself"
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

    if response.status_code == 200:

        user = response.json()

        print("Jira connection successful!")
        print(
            f"Account ID: "
            f"{user.get('accountId')}"
        )

        print(
            f"Display name: "
            f"{user.get('displayName')}"
        )

    else:

        print(
            "Jira connection failed."
        )

        print(
            f"Response: {response.text}"
        )


if __name__ == "__main__":
    test_jira_connection()