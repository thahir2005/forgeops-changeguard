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

        blast_radius = self._analyze_blast_radius(
            owner=owner,
            repo=repo,
            head_sha=head_sha,
            changed_files=changed_files,
        )

        analysis = analyze_change(
            changed_files=changed_files,
            diffs=diffs,
            directly_affected_services=(
                blast_radius["directly_affected_services"]
            ),
            transitively_affected_services=(
                blast_radius["transitively_affected_services"]
            ),
        )

        analysis["blast_radius"] = blast_radius

        # ---------------------------------------------
        # Analyze infrastructure dependencies
        # ---------------------------------------------



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
        Build a repository-wide Kubernetes dependency graph
        from the PR HEAD and calculate blast radius.

        Dependencies are discovered only from explicit
        Kubernetes references. No dependencies are guessed.
        """

        service = BlastRadiusService()

        discovered_dependencies = []
        manifests_analyzed = []

        # ---------------------------------------------
        # Discover all repository files at PR HEAD
        # ---------------------------------------------

        try:
            repository_files = (
                self.github.get_repository_files(
                    owner=owner,
                    repo=repo,
                    ref=head_sha,
                )
            )

        except Exception as exc:
            return {
                "status": "unavailable",
                "reason": (
                    "Unable to list repository files: "
                    f"{exc}"
                ),
                "dependencies_discovered": 0,
                "dependencies": [],
                "affected_services": [],
                "manifests_analyzed": [],
            }

        # ---------------------------------------------
        # Select Kubernetes manifests
        # ---------------------------------------------

        kubernetes_files = [
            path
            for path in repository_files
            if (
                path.endswith(".yaml")
                or path.endswith(".yml")
            )
        ]

        # ---------------------------------------------
        # Build repository-wide dependency graph
        # ---------------------------------------------

        for file_path in kubernetes_files:

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
                        "Unable to retrieve Kubernetes "
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
                manifest = yaml.safe_load(content)

            except yaml.YAMLError as exc:
                return {
                    "status": "unavailable",
                    "reason": (
                        f"Invalid YAML in '{file_path}': "
                        f"{exc}"
                    ),
                    "dependencies_discovered": 0,
                    "dependencies": [],
                    "affected_services": [],
                    "manifests_analyzed": [],
                }

            if not isinstance(manifest, dict):
                continue

            if manifest.get("kind") != "Deployment":
                continue

            manifests_analyzed.append(file_path)

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
        # Identify resources affected by this PR
        # ---------------------------------------------

        changed_kubernetes_files = {
            path
            for path in changed_files
            if (
                path.endswith(".yaml")
                or path.endswith(".yml")
            )
        }

        changed_services = set()

        for dependency in discovered_dependencies:

            source_service = dependency["service"]

            # If the service's Kubernetes manifest changed,
            # it is a changed resource we can analyze.
            #
            # The repository-wide graph has already been built,
            # so transitive dependents can now be calculated.
            for file_path in changed_kubernetes_files:

                if file_path.endswith(
                    f"{source_service}.yaml"
                ) or file_path.endswith(
                    f"{source_service}.yml"
                ):
                    changed_services.add(
                        source_service
                    )

        # ---------------------------------------------
        # Also identify changed Deployment manifests
        # directly from their file contents.
        # ---------------------------------------------

        for file_path in changed_kubernetes_files:

            try:
                content = self.github.get_file_content(
                    owner=owner,
                    repo=repo,
                    path=file_path,
                    ref=head_sha,
                )

                manifest = yaml.safe_load(content)

            except (
                Exception,
                yaml.YAMLError,
            ):
                continue

            if not isinstance(manifest, dict):
                continue

            if manifest.get("kind") != "Deployment":
                continue

            metadata = manifest.get(
                "metadata",
                {},
            )

            service_name = metadata.get("name")

            if service_name:
                changed_services.add(
                    service_name
                )

        # ---------------------------------------------
        # Calculate repository-wide blast radius
        # ---------------------------------------------

        directly_affected_services = set()
        transitively_affected_services = set()

        for changed_resource in changed_services:

            impact = service.get_impact_levels(
                changed_resource
            )

            directly_affected_services.update(
                impact.get(
                    "directly_affected",
                    [],
                )
            )

            transitively_affected_services.update(
                impact.get(
                    "transitively_affected",
                    [],
                )
            )

        # A service that is directly affected should not also
        # appear in the transitive set.
                # A service classified as direct should never also appear
        # as transitive.
        transitively_affected_services -= (
            directly_affected_services
        )

        affected_services = (
            directly_affected_services
            | transitively_affected_services
        )

        return {
            "status": "success",
            "dependencies_discovered": (
                len(discovered_dependencies)
            ),
            "dependencies": (
                discovered_dependencies
            ),
            "directly_affected_services": sorted(
                directly_affected_services
            ),
            "transitively_affected_services": sorted(
                transitively_affected_services
            ),
            "affected_services": sorted(
                affected_services
            ),
            "blast_radius_count": len(
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
