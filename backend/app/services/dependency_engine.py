from collections import defaultdict


class DependencyGraph:
    def __init__(self):
        self.dependencies = defaultdict(set)

    def add_dependency(
        self,
        service: str,
        dependency: str,
    ):
        """
        Register that a service depends on another resource.
        """

        self.dependencies[service].add(dependency)

    def get_dependencies(
        self,
        service: str,
    ) -> list[str]:
        """
        Return direct dependencies of a service.
        """

        return sorted(
            self.dependencies.get(service, set())
        )

    def get_affected_services(
        self,
        changed_resource: str,
    ) -> list[str]:
        """
        Find services directly affected by a changed resource.
        """

        affected = []

        for service, dependencies in self.dependencies.items():

            if changed_resource in dependencies:
                affected.append(service)

        return sorted(affected)
