from typing import Any

from app.services.github_service import GitHubService
from app.services.change_service import analyze_change


class PRAnalysisService:
    """
    Orchestrates GitHub pull-request retrieval
    and ForgeOps change analysis.
    """

    def __init__(
        self,
        github_service: GitHubService | None = None,
    ):
        self.github = (
            github_service
            if github_service is not None
            else GitHubService()
        )

    def analyze_pull_request(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> dict[str, Any]:

        # ---------------------------------------------
        # Get PR metadata
        # ---------------------------------------------

        pr = self.github.get_pull_request(
            owner,
            repo,
            pull_number,
        )

        # ---------------------------------------------
        # Get changed files
        # ---------------------------------------------

        github_files = self.github.get_changed_files(
            owner,
            repo,
            pull_number,
        )

        changed_files = [
            file["filename"]
            for file in github_files
        ]

        # ---------------------------------------------
        # Get complete PR diff
        # ---------------------------------------------

        full_diff = self.github.get_pull_request_diff(
            owner,
            repo,
            pull_number,
        )

        # ---------------------------------------------
        # Split unified diff by file
        # ---------------------------------------------

        diffs = self._split_diff_by_file(
            full_diff
        )

        # ---------------------------------------------
        # Run ForgeOps analysis
        # ---------------------------------------------

        analysis = analyze_change(
            changed_files=changed_files,
            diffs=diffs,
        )

        # ---------------------------------------------
        # Add GitHub context
        # ---------------------------------------------

        return {
            "repository": f"{owner}/{repo}",

            "pull_request": {
                "number": pr["number"],
                "title": pr["title"],
                "state": pr["state"],
                "author": pr["user"]["login"],
                "base_branch": pr["base"]["ref"],
                "head_branch": pr["head"]["ref"],
                "url": pr["html_url"],
            },

            "analysis": analysis,
        }

    @staticmethod
    def _split_diff_by_file(
        diff: str,
    ) -> dict[str, str]:
        """
        Split a GitHub unified diff into
        individual file diffs.
        """

        diffs: dict[str, str] = {}

        current_file: str | None = None
        current_lines: list[str] = []

        for line in diff.splitlines():

            if line.startswith("diff --git "):

                # Save previous file
                if current_file is not None:
                    diffs[current_file] = (
                        "\n".join(current_lines)
                    )

                current_lines = []

                # Example:
                #
                # diff --git a/file.tf b/file.tf
                #
                parts = line.split()

                if len(parts) >= 4:
                    current_file = parts[3]

                    if current_file.startswith("b/"):
                        current_file = (
                            current_file[2:]
                        )

                current_lines.append(line)

            else:

                current_lines.append(line)

        # Save final file
        if current_file is not None:
            diffs[current_file] = (
                "\n".join(current_lines)
            )

        return diffs
