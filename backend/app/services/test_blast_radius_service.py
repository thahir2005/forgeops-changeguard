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
                ]
            }
        },
    },
}


service = BlastRadiusService()

print("ForgeOps Blast Radius Analysis")
print("===============================")

dependencies = (
    service.add_kubernetes_manifest(
        manifest
    )
)

print("\nDiscovered Dependencies")
print("-----------------------")

for dependency in dependencies:

    print(
        f"{dependency['service']} "
        f"-> {dependency['dependency']}"
    )

print("\nBlast Radius")
print("------------")

# Demonstrate downstream dependency
service.graph.add_dependency(
    "checkout-service",
    "payment-api",
)

service.graph.add_dependency(
    "order-service",
    "payment-api",
)

for affected in service.get_blast_radius(
    "postgres-db"
):

    print("-", affected)
