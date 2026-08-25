import base64
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

    def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str,
    ) -> str:
        """
        Retrieve the complete contents of a repository file
        at a specific Git reference.

        This is used for infrastructure analysis because a PR
        diff may contain only a few changed lines while the
        complete Kubernetes/Terraform file contains the context
        required for dependency analysis.
        """

        url = (
            f"{self.base_url}/repos/"
            f"{owner}/{repo}/contents/{path}"
        )

        params = {
            "ref": ref,
        }

        response = httpx.get(
            url,
            headers=self.headers,
            params=params,
            timeout=30.0,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("encoding") != "base64":
            raise RuntimeError(
                f"Unsupported GitHub file encoding for: {path}"
            )

        encoded_content = data.get("content", "")

        # GitHub may include line breaks in the Base64 payload.
        encoded_content = encoded_content.replace(
            "\n",
            "",
        )

        try:
            decoded_content = base64.b64decode(
                encoded_content
            ).decode("utf-8")

        except (ValueError, UnicodeDecodeError) as exc:
            raise RuntimeError(
                f"Unable to decode GitHub file: {path}"
            ) from exc

        return decoded_content
