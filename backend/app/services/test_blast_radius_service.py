from app.services.blast_radius_service import (
    BlastRadiusService,
)


manifest = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {
        "name": "payment-api",
    },
    "spec": {
        "template": {
            "spec": {
                "containers": [
                    {
                        "name": "payment-api",
                        "image": "payment-api:v1.5",
                        "env": [
                            {
                                "name": "DATABASE_HOST",
                                "value": "postgres-db",
                            },
                            {
                                "name": "REDIS_HOST",
                                "value": "redis",
                            },
                        ],
                    }
                ],
            },
        },
    },
}


service = BlastRadiusService()


# -------------------------------------------------
# Dependency discovery
# -------------------------------------------------

dependencies = service.add_kubernetes_manifest(
    manifest
)

assert len(dependencies) == 2

assert {
    "service": "payment-api",
    "dependency": "postgres-db",
    "source": "env:DATABASE_HOST",
} in dependencies

assert {
    "service": "payment-api",
    "dependency": "redis",
    "source": "env:REDIS_HOST",
} in dependencies


# -------------------------------------------------
# Build downstream dependency graph
# -------------------------------------------------

service.graph.add_dependency(
    "checkout-service",
    "payment-api",
)

service.graph.add_dependency(
    "order-service",
    "payment-api",
)


# -------------------------------------------------
# Direct impact
# -------------------------------------------------

direct = service.graph.get_impact_levels(
    "postgres-db"
)

assert direct["directly_affected"] == [
    "payment-api"
]


# -------------------------------------------------
# Transitive impact
# -------------------------------------------------

assert direct["transitively_affected"] == [
    "checkout-service",
    "order-service",
]


# -------------------------------------------------
# Total blast radius
# -------------------------------------------------

assert direct["total_affected"] == [
    "checkout-service",
    "order-service",
    "payment-api",
]


blast_radius = service.get_blast_radius(
    "postgres-db"
)

assert blast_radius == [
    "checkout-service",
    "order-service",
    "payment-api",
]


# -------------------------------------------------
# Final output
# -------------------------------------------------

print("ForgeOps Blast Radius Analysis")
print("===============================")

print()
print("Discovered Dependencies")
print("-----------------------")

for dependency in dependencies:
    print(
        f"- {dependency['service']} "
        f"-> {dependency['dependency']} "
        f"({dependency['source']})"
    )

print()
print("Directly Affected")
print("-----------------")

for service_name in direct["directly_affected"]:
    print(f"- {service_name}")

print()
print("Transitively Affected")
print("---------------------")

for service_name in direct["transitively_affected"]:
    print(f"- {service_name}")

print()
print("Total Blast Radius")
print("------------------")

for service_name in direct["total_affected"]:
    print(f"- {service_name}")

print()
print(
    f"Blast Radius Count: "
    f"{len(direct['total_affected'])}"
)

print()
print("All blast radius assertions passed.")
