def generate_recommendations(
    terraform_impacts: list[dict],
    kubernetes_impacts: list[dict],
    security_findings: list[dict],
    directly_affected_services: list[str] | None = None,
    transitively_affected_services: list[str] | None = None,
) -> list[str]:
    """
    Generate actionable recommendations from
    existing ForgeOps risk signals.
    """

    recommendations = []

    directly_affected_services = (
        directly_affected_services or []
    )

    transitively_affected_services = (
        transitively_affected_services or []
    )

    # -------------------------------------------------
    # Terraform recommendations
    # -------------------------------------------------

    for impact in terraform_impacts:

        reasons = impact.get("reasons", [])

        for reason in reasons:

            if "instance" in reason.lower():
                recommendations.append(
                    "Review the infrastructure size change "
                    "and validate the expected production "
                    "workload before deployment."
                )

            if "cost" in reason.lower():
                recommendations.append(
                    "Review the expected infrastructure cost "
                    "increase before deployment."
                )

    # -------------------------------------------------
    # Kubernetes recommendations
    # -------------------------------------------------

    for impact in kubernetes_impacts:

        reasons = impact.get("reasons", [])

        for reason in reasons:

            normalized = reason.lower()

            if "replica count decreases" in normalized:
                recommendations.append(
                    "Restore the affected service to at least "
                    "2 replicas unless single-replica operation "
                    "is explicitly approved."
                )

            if (
                "lower memory limit" in normalized
                or "out-of-memory" in normalized
            ):
                recommendations.append(
                    "Validate memory requirements and monitor "
                    "for out-of-memory termination before "
                    "production rollout."
                )

            if (
                "lower cpu limit" in normalized
                or "cpu throttling" in normalized
            ):
                recommendations.append(
                    "Validate CPU requirements and test for "
                    "CPU throttling under expected production load."
                )

            if "container image changes" in normalized:
                recommendations.append(
                    "Validate the new container image with "
                    "automated tests before production rollout."
                )

    # -------------------------------------------------
    # Security recommendations
    # -------------------------------------------------

    for finding in security_findings:

        severity = finding.get(
            "severity",
            "low",
        )

        if severity in {"high", "critical"}:
            recommendations.append(
                "Resolve high-severity security findings "
                "before production deployment."
            )
        else:
            recommendations.append(
                "Review the detected security finding "
                "before deployment."
            )

    # -------------------------------------------------
    # Dependency recommendations
    # -------------------------------------------------

    total_affected = (
        len(directly_affected_services)
        + len(transitively_affected_services)
    )

    if total_affected >= 3:
        recommendations.append(
            "Validate all affected services together "
            "because the change has a broad dependency blast radius."
        )
    elif total_affected > 0:
        recommendations.append(
            "Validate directly affected services before "
            "production deployment."
        )

    # -------------------------------------------------
    # Remove duplicates while preserving order
    # -------------------------------------------------

    unique_recommendations = []

    for recommendation in recommendations:

        if recommendation not in unique_recommendations:
            unique_recommendations.append(
                recommendation
            )

    return unique_recommendations
