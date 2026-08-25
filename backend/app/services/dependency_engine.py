from collections import defaultdict, deque


class DependencyGraph:
    """
    Dependency graph for service/resource relationships.

    Example:

        payment-api -> postgres-db
        payment-api -> redis
        order-service -> payment-api

    This means:
        payment-api depends on postgres-db
        order-service depends on payment-api
    """

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
        Return services that directly depend on
        the changed resource.
        """

        affected = []

        for service, dependencies in self.dependencies.items():

            if changed_resource in dependencies:
                affected.append(service)

        return sorted(affected)

    def get_blast_radius(
        self,
        changed_resource: str,
    ) -> list[str]:
        """
        Return all services potentially affected by
        a changed resource, including transitive dependents.
        """

        return self.get_impact_levels(
            changed_resource
        )["total_affected"]


    def get_impact_levels(
        self,
        changed_resource: str,
    ) -> dict[str, list[str]]:
        """
        Classify affected services into direct and
        transitive dependents.
        """

        directly_affected = set(
            self.get_affected_services(
                changed_resource
            )
        )

        transitively_affected = set()

        queue = deque(directly_affected)

        while queue:

            resource = queue.popleft()

            for service, dependencies in self.dependencies.items():

                if (
                    resource in dependencies
                    and service not in directly_affected
                    and service not in transitively_affected
                ):
                    transitively_affected.add(service)
                    queue.append(service)

        total_affected = (
            directly_affected
            | transitively_affected
        )

        return {
            "directly_affected": sorted(
                directly_affected
            ),
            "transitively_affected": sorted(
                transitively_affected
            ),
            "total_affected": sorted(
                total_affected
            ),
        }

    def get_impact_levels(
        self,
        changed_resource: str,
    ) -> dict[str, list[str]]:
        """
        Return direct and transitive impact separately.

        Example:

            postgres-db
                ↓
            payment-api
                ↓
            checkout-service

        Returns:

            {
                "directly_affected": [
                    "payment-api"
                ],
                "transitively_affected": [
                    "checkout-service"
                ],
                "total_affected": [
                    "checkout-service",
                    "payment-api"
                ]
            }
        """

        directly_affected = set(
            self.get_affected_services(
                changed_resource
            )
        )

        transitively_affected = set()

        queue = deque(
            directly_affected
        )

        visited = set(
            directly_affected
        )

        while queue:

            resource = queue.popleft()

            for service, dependencies in self.dependencies.items():

                if (
                    resource in dependencies
                    and service not in visited
                ):
                    visited.add(service)
                    transitively_affected.add(
                        service
                    )
                    queue.append(service)

        total_affected = (
            directly_affected
            | transitively_affected
        )

        return {
            "directly_affected": sorted(
                directly_affected
            ),
            "transitively_affected": sorted(
                transitively_affected
            ),
            "total_affected": sorted(
                total_affected
            ),
        }