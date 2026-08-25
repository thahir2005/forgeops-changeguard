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

        impact["performance"] = "medium"

        impact["reasons"].append(
            f"Memory limit changes from "
            f"{old_value} to {new_value}."
        )

        impact["reasons"].append(
            "A lower memory limit can increase "
            "the risk of out-of-memory termination."
        )

    # -------------------------------------------------
    # CPU changes
    # -------------------------------------------------

    elif attribute == "cpu_limit":

        impact["performance"] = "medium"

        impact["reasons"].append(
            f"CPU limit changes from "
            f"{old_value} to {new_value}."
        )

        impact["reasons"].append(
            "A lower CPU limit can cause "
            "CPU throttling under load."
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
