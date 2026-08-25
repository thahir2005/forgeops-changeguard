from typing import Any


DEPENDENCY_ENV_NAMES = {
    "DATABASE_HOST",
    "DATABASE_URL",
    "DB_HOST",
    "REDIS_HOST",
    "REDIS_URL",
    "KAFKA_HOST",
    "KAFKA_BROKERS",
    "BROKER_URL",

    # Explicit service-to-service dependencies
    "PAYMENT_API_HOST",
}


def discover_kubernetes_dependencies(
    manifest: dict[str, Any],
) -> list[dict[str, str]]:
    """
    Discover explicitly declared dependencies from a
    Kubernetes Deployment manifest.

    This analyzer intentionally avoids guessing dependencies.
    A dependency is reported only when the manifest explicitly
    references another resource.
    """

    dependencies: list[dict[str, str]] = []

    kind = manifest.get("kind")

    if kind != "Deployment":
        return dependencies

    metadata = manifest.get("metadata", {})
    service_name = metadata.get("name")

    if not service_name:
        return dependencies

    spec = manifest.get("spec", {})
    template = spec.get("template", {})
    pod_spec = template.get("spec", {})

    containers = pod_spec.get("containers", [])

    for container in containers:

        # ---------------------------------------------
        # Direct environment variables
        # ---------------------------------------------

        for env in container.get("env", []):

            name = env.get("name")

            if name not in DEPENDENCY_ENV_NAMES:
                continue

            value = env.get("value")

            if value:
                dependencies.append(
                    {
                        "service": service_name,
                        "dependency": value,
                        "source": f"env:{name}",
                    }
                )

        # ---------------------------------------------
        # ConfigMap references
        # ---------------------------------------------

        for env_from in container.get("envFrom", []):

            config_map = env_from.get("configMapRef")

            if config_map:
                name = config_map.get("name")

                if name:
                    dependencies.append(
                        {
                            "service": service_name,
                            "dependency": name,
                            "source": "configMapRef",
                        }
                    )

            secret = env_from.get("secretRef")

            if secret:
                name = secret.get("name")

                if name:
                    dependencies.append(
                        {
                            "service": service_name,
                            "dependency": name,
                            "source": "secretRef",
                        }
                    )

    # ---------------------------------------------
    # Deduplicate dependencies
    # ---------------------------------------------

    unique = {
        (
            item["service"],
            item["dependency"],
            item["source"],
        ): item
        for item in dependencies
    }

    return list(unique.values())
