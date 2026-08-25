def _parse_memory(value: str) -> int:
    """
    Convert Kubernetes memory quantities into bytes.
    """

    value = str(value).strip()

    units = {
        "Ki": 1024,
        "Mi": 1024 ** 2,
        "Gi": 1024 ** 3,
        "Ti": 1024 ** 4,
    }

    for suffix, multiplier in units.items():

        if value.endswith(suffix):
            number = float(
                value[:-len(suffix)]
            )

            return int(
                number * multiplier
            )

    return int(float(value))


def _parse_cpu(value: str) -> float:
    """
    Convert Kubernetes CPU quantities into millicores.
    """

    value = str(value).strip()

    if value.endswith("m"):
        return float(
            value[:-1]
        )

    return float(value) * 1000


def analyze_kubernetes_impact(change: dict) -> dict:
    """
    Determine potential operational impact
    of a Kubernetes change.
    """

    attribute = change.get("attribute")
    old_value = change.get("old_value")
    new_value = change.get("new_value")

    impact = {
        "reliability": "low",
        "cost": "low",
        "performance": "low",
        "deployment": "low",
        "reasons": [],
    }

    # -------------------------------------------------
    # Replica changes
    # -------------------------------------------------

    if attribute == "replicas":

        old_replicas = int(old_value)
        new_replicas = int(new_value)

        if new_replicas < old_replicas:

            impact["reliability"] = "high"

            impact["reasons"].append(
                f"Replica count decreases from "
                f"{old_replicas} to {new_replicas}."
            )

            if new_replicas == 1:

                impact["reliability"] = "high"

                impact["reasons"].append(
                    "Running a single replica removes "
                    "application redundancy."
                )

        elif new_replicas > old_replicas:

            impact["cost"] = "medium"
            impact["performance"] = "medium"

            impact["reasons"].append(
                f"Replica count increases from "
                f"{old_replicas} to {new_replicas}."
            )

            impact["reasons"].append(
                "Additional replicas may increase "
                "compute resource consumption."
            )

    # -------------------------------------------------
    # Memory changes
    # -------------------------------------------------

    elif attribute == "memory_limit":

        old_memory = _parse_memory(
            old_value
        )

        new_memory = _parse_memory(
            new_value
        )

        impact["reasons"].append(
            f"Memory limit changes from "
            f"{old_value} to {new_value}."
        )

        if new_memory < old_memory:

            impact["reliability"] = "medium"
            impact["performance"] = "medium"

            impact["reasons"].append(
                "A lower memory limit can increase "
                "the risk of out-of-memory termination."
            )

        elif new_memory > old_memory:

            impact["cost"] = "medium"

            impact["reasons"].append(
                "A higher memory limit may increase "
                "resource consumption and infrastructure cost."
            )

    # -------------------------------------------------
    # CPU changes
    # -------------------------------------------------

    elif attribute == "cpu_limit":

        old_cpu = _parse_cpu(
            old_value
        )

        new_cpu = _parse_cpu(
            new_value
        )

        impact["reasons"].append(
            f"CPU limit changes from "
            f"{old_value} to {new_value}."
        )

        if new_cpu < old_cpu:

            impact["reliability"] = "medium"
            impact["performance"] = "medium"

            impact["reasons"].append(
                "A lower CPU limit can cause "
                "CPU throttling under load."
            )

        elif new_cpu > old_cpu:

            impact["cost"] = "medium"

            impact["reasons"].append(
                "A higher CPU limit may increase "
                "resource consumption and infrastructure cost."
            )

    # -------------------------------------------------
    # Container image changes
    # -------------------------------------------------

    elif attribute == "image":

        impact["deployment"] = "medium"

        impact["reasons"].append(
            f"Container image changes from "
            f"{old_value} to {new_value}."
        )

        impact["reasons"].append(
            "The new image should be validated "
            "before production rollout."
        )

    return impact