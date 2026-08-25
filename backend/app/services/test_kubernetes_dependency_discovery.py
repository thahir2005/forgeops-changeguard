from app.services.kubernetes_dependency_discovery import (
    discover_kubernetes_dependencies,
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
        }
    },
}


print("ForgeOps Kubernetes Dependency Discovery")
print("=========================================")

dependencies = discover_kubernetes_dependencies(
    manifest
)

if not dependencies:
    print("No dependencies discovered.")
else:
    for dependency in dependencies:
        print(
            f"{dependency['service']} "
            f"-> {dependency['dependency']} "
            f"({dependency['source']})"
        )
