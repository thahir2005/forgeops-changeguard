RISK_VALUES = {
    "low": 20,
    "medium": 50,
    "high": 80,
    "critical": 100,
}


def calculate_blast_radius_score(
    directly_affected: int,
    transitively_affected: int,
) -> int:
    """
    Calculate a risk score from dependency blast radius.
    """

    total_affected = (
        directly_affected
        + transitively_affected
    )

    if total_affected == 0:
        return 0

    if total_affected >= 6:
        base_score = 80
    elif total_affected >= 4:
        base_score = 60
    elif total_affected >= 2:
        base_score = 40
    else:
        base_score = 20

    if transitively_affected >= 3:
        base_score += 20
    elif transitively_affected >= 1:
        base_score += 10

    return min(base_score, 100)


def _deduplicate_reasons(
    reasons: list[str],
) -> list[str]:
    """
    Remove duplicate risk explanations while preserving
    their original order.
    """

    seen = set()
    unique_reasons = []

    for reason in reasons:
        normalized = reason.strip()

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)
        unique_reasons.append(normalized)

    return unique_reasons


def determine_risk_decision(
    overall_score: int,
) -> dict:
    """
    Convert the overall risk score into an
    actionable deployment decision.
    """

    if overall_score >= 76:
        return {
            "decision": "block",
            "label": "BLOCK",
            "message": (
                "This change should not proceed "
                "without risk mitigation."
            ),
        }

    if overall_score >= 26:
        return {
            "decision": "review_required",
            "label": "REVIEW REQUIRED",
            "message": (
                "This change requires review "
                "before deployment."
            ),
        }

    return {
        "decision": "safe",
        "label": "SAFE",
        "message": (
            "No significant risk was detected. "
            "The change can proceed."
        ),
    }


def calculate_overall_risk(
    terraform_impacts: list[dict],
    kubernetes_impacts: list[dict],
    security_findings: list[dict],
    directly_affected_services: list[str] | None = None,
    transitively_affected_services: list[str] | None = None,
) -> dict:
    """
    Combine infrastructure, Kubernetes, security,
    and dependency blast-radius signals into one
    risk assessment.
    """

    directly_affected_services = (
        directly_affected_services or []
    )

    transitively_affected_services = (
        transitively_affected_services or []
    )

    reliability_scores = []
    security_scores = []
    cost_scores = []

    reasons = []

    # -------------------------------------------------
    # Terraform
    # -------------------------------------------------

    for impact in terraform_impacts:

        cost = impact.get("cost", "low")
        reliability = impact.get("reliability", "low")
        security = impact.get("security", "low")

        cost_scores.append(
            RISK_VALUES[cost]
        )

        reliability_scores.append(
            RISK_VALUES[reliability]
        )

        security_scores.append(
            RISK_VALUES[security]
        )

        reasons.extend(
            impact.get("reasons", [])
        )

    # -------------------------------------------------
    # Kubernetes
    # -------------------------------------------------

    for impact in kubernetes_impacts:

        cost = impact.get("cost", "low")
        reliability = impact.get("reliability", "low")

        cost_scores.append(
            RISK_VALUES[cost]
        )

        reliability_scores.append(
            RISK_VALUES[reliability]
        )

        reasons.extend(
            impact.get("reasons", [])
        )

    # -------------------------------------------------
    # Security
    # -------------------------------------------------

    for finding in security_findings:

        severity = finding.get(
            "severity",
            "low",
        )

        security_scores.append(
            RISK_VALUES[severity]
        )

        reasons.append(
            finding.get(
                "message",
                "Security issue detected.",
            )
        )

    # -------------------------------------------------
    # Blast radius
    # -------------------------------------------------

    blast_radius_score = calculate_blast_radius_score(
        directly_affected=len(
            directly_affected_services
        ),
        transitively_affected=len(
            transitively_affected_services
        ),
    )

    if blast_radius_score > 0:
        total_affected = (
            len(directly_affected_services)
            + len(transitively_affected_services)
        )

        reasons.append(
            "Dependency blast radius affects "
            f"{total_affected} service(s)."
        )

    if directly_affected_services:
        reasons.append(
            "Direct dependency impact affects "
            f"{len(directly_affected_services)} service(s)."
        )

    if transitively_affected_services:
        reasons.append(
            "Transitive dependency impact indicates "
            "potential cascading operational effects."
        )

    # -------------------------------------------------
    # Remove duplicate explanations
    # -------------------------------------------------

    reasons = _deduplicate_reasons(reasons)

    # -------------------------------------------------
    # Maximum signal per category
    # -------------------------------------------------

    reliability_score = (
        max(reliability_scores)
        if reliability_scores
        else 0
    )

    security_score = (
        max(security_scores)
        if security_scores
        else 0
    )

    cost_score = (
        max(cost_scores)
        if cost_scores
        else 0
    )

    # -------------------------------------------------
    # Blast radius contributes to reliability
    # -------------------------------------------------

    reliability_score = max(
        reliability_score,
        blast_radius_score,
    )

    # -------------------------------------------------
    # Overall risk
    # -------------------------------------------------

    overall_score = round(
        (
            reliability_score * 0.4
            + security_score * 0.3
            + cost_score * 0.3
        )
    )

    # -------------------------------------------------
    # Risk category
    # -------------------------------------------------

    if overall_score >= 76:
        category = "critical"

    elif overall_score >= 51:
        category = "high"

    elif overall_score >= 26:
        category = "medium"

    else:
        category = "low"

    decision = determine_risk_decision(
    overall_score
    )

    return {
        "overall_score": overall_score,
        "category": category,
        "reliability_score": reliability_score,
        "security_score": security_score,
        "cost_score": cost_score,
        "blast_radius_score": blast_radius_score,
        "reasons": reasons,

        "decision": decision["decision"],
        "decision_label": decision["label"],
        "decision_message": decision["message"],
    }
