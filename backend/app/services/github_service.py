import os
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv()


class GitHubService:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = os.getenv(
            "GITHUB_API_URL",
            "https://api.github.com",
        )

        if not self.token:
            raise RuntimeError(
                "GITHUB_TOKEN is not configured."
            )

        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def get_pull_request(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> dict[str, Any]:

        url = (
            f"{self.base_url}/repos/"
            f"{owner}/{repo}/pulls/{pull_number}"
        )

        response = httpx.get(
            url,
            headers=self.headers,
            timeout=30.0,
        )

        response.raise_for_status()

        return response.json()

    def get_changed_files(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> list[dict[str, Any]]:

        url = (
            f"{self.base_url}/repos/"
            f"{owner}/{repo}/pulls/{pull_number}/files"
        )

        response = httpx.get(
            url,
            headers=self.headers,
            timeout=30.0,
        )

        response.raise_for_status()

        return response.json()

    def get_pull_request_diff(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> str:

        url = (
            f"{self.base_url}/repos/"
            f"{owner}/{repo}/pulls/{pull_number}"
        )

        headers = {
            **self.headers,
            "Accept": "application/vnd.github.diff",
        }

        response = httpx.get(
            url,
            headers=headers,
            timeout=30.0,
        )

        response.raise_for_status()

        return response.text
