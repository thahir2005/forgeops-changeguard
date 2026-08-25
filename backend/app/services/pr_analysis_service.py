from typing import Any

import yaml

from app.services.github_service import GitHubService
from app.services.change_service import analyze_change
from app.services.blast_radius_service import BlastRadiusService


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

        head_sha = pr["head"]["sha"]

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
        # Run ForgeOps change analysis
        # ---------------------------------------------

        analysis = analyze_change(
            changed_files=changed_files,
            diffs=diffs,
        )

        # ---------------------------------------------
        # Analyze infrastructure dependencies
        # ---------------------------------------------

        blast_radius = self._analyze_blast_radius(
            owner=owner,
            repo=repo,
            head_sha=head_sha,
            changed_files=changed_files,
        )

        analysis["blast_radius"] = blast_radius

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
                "head_sha": head_sha,
            },

            "analysis": analysis,
        }

    def _analyze_blast_radius(
        self,
        owner: str,
        repo: str,
        head_sha: str,
        changed_files: list[str],
    ) -> dict[str, Any]:
        """
        Fetch complete Kubernetes manifests from the PR head,
        discover explicitly declared dependencies, and calculate
        their blast radius.

        Dependencies are never guessed.
        """

        service = BlastRadiusService()

        discovered_dependencies = []
        manifests_analyzed = []

        for file_path in changed_files:

            if not (
                file_path.endswith(".yaml")
                or file_path.endswith(".yml")
            ):
                continue

            # -----------------------------------------
            # Fetch complete file from PR HEAD
            # -----------------------------------------

            try:
                content = self.github.get_file_content(
                    owner=owner,
                    repo=repo,
                    path=file_path,
                    ref=head_sha,
                )

            except Exception as exc:
                return {
                    "status": "unavailable",
                    "reason": (
                        f"Unable to retrieve Kubernetes "
                        f"manifest '{file_path}': {exc}"
                    ),
                    "dependencies_discovered": 0,
                    "dependencies": [],
                    "affected_services": [],
                    "manifests_analyzed": [],
                }

            # -----------------------------------------
            # Parse YAML
            # -----------------------------------------

            try:
                manifest = yaml.safe_load(
                    content
                )

            except yaml.YAMLError:
                continue

            if not isinstance(
                manifest,
                dict,
            ):
                continue

            if manifest.get("kind") != "Deployment":
                continue

            manifests_analyzed.append(
                file_path
            )

            # -----------------------------------------
            # Discover dependencies
            # -----------------------------------------

            dependencies = (
                service.add_kubernetes_manifest(
                    manifest
                )
            )

            discovered_dependencies.extend(
                dependencies
            )

        # ---------------------------------------------
        # Calculate affected services
        # ---------------------------------------------

        affected_services = set()

        for dependency in discovered_dependencies:

            dependency_name = dependency[
                "dependency"
            ]

            affected = (
                service.get_blast_radius(
                    dependency_name
                )
            )

            affected_services.update(
                affected
            )

        return {
            "status": "success",
            "dependencies_discovered": (
                len(discovered_dependencies)
            ),
            "dependencies": (
                discovered_dependencies
            ),
            "affected_services": sorted(
                affected_services
            ),
            "manifests_analyzed": (
                manifests_analyzed
            ),
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

                if current_file is not None:
                    diffs[current_file] = (
                        "\n".join(current_lines)
                    )

                current_lines = []

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

        if current_file is not None:
            diffs[current_file] = (
                "\n".join(current_lines)
            )

        return diffs
