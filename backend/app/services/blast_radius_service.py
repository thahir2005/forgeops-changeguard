from typing import Any

from app.services.dependency_engine import DependencyGraph
from app.services.kubernetes_dependency_discovery import (
    discover_kubernetes_dependencies,
)


class BlastRadiusService:
    """
    Builds a dependency graph from discovered infrastructure
    dependencies and calculates the potential blast radius.
    """

    def __init__(
        self,
        graph: DependencyGraph | None = None,
    ):
        self.graph = (
            graph
            if graph is not None
            else DependencyGraph()
        )

    def add_kubernetes_manifest(
        self,
        manifest: dict[str, Any],
    ) -> list[dict[str, str]]:
        """
        Discover dependencies from a Kubernetes manifest
        and add them to the dependency graph.
        """

        dependencies = (
            discover_kubernetes_dependencies(
                manifest
            )
        )

        for item in dependencies:

            self.graph.add_dependency(
                item["service"],
                item["dependency"],
            )

        return dependencies

    def get_blast_radius(
        self,
        changed_resource: str,
    ) -> list[str]:
        """
        Calculate all direct and transitive services
        affected by a changed resource.
        """

        return self.graph.get_blast_radius(
            changed_resource
        )

    def get_impact_levels(
        self,
        changed_resource: str,
    ) -> dict[str, list[str]]:
        """
        Return direct and transitive services affected
        by a changed resource.
        """

        return self.graph.get_impact_levels(
            changed_resource
        )

    def get_impact_levels(
        self,
        changed_resource: str,
    ) -> dict[str, list[str]]:
        """
        Return direct and transitive impact separately.
        """

        return self.graph.get_impact_levels(
            changed_resource
        )