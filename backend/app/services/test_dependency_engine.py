from app.services.dependency_engine import DependencyGraph


graph = DependencyGraph()


graph.add_dependency(
    "payment-api",
    "postgres-db",
)

graph.add_dependency(
    "payment-api",
    "redis",
)

graph.add_dependency(
    "order-service",
    "postgres-db",
)

graph.add_dependency(
    "order-service",
    "kafka",
)


print("ForgeOps Dependency Graph")
print("=========================")

print("\npayment-api depends on:")

for dependency in graph.get_dependencies("payment-api"):
    print("-", dependency)


print("\nServices affected by postgres-db:")

for service in graph.get_affected_services("postgres-db"):
    print("-", service)
