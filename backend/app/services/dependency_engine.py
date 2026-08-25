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

        Example:

            database
                ↓
            payment-api
                ↓
            checkout-service

        Changing database returns:

            payment-api
            checkout-service
        """

        affected = set()
        queue = deque([changed_resource])

        while queue:

            resource = queue.popleft()

            for service, dependencies in self.dependencies.items():

                if (
                    resource in dependencies
                    and service not in affected
                ):
                    affected.add(service)
                    queue.append(service)

        return sorted(affected)
