RISK_VALUES = {
    "low": 20,
    "medium": 50,
    "high": 80,
    "critical": 100,
}


def calculate_overall_risk(
    terraform_impacts: list[dict],
    kubernetes_impacts: list[dict],
    security_findings: list[dict],
) -> dict:
    """
    Combine infrastructure, Kubernetes,
    and security signals into one risk assessment.
    """

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

        cost_scores.append(RISK_VALUES[cost])
        reliability_scores.append(RISK_VALUES[reliability])
        security_scores.append(RISK_VALUES[security])

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

    return {
        "overall_score": overall_score,
        "category": category,
        "reliability_score": reliability_score,
        "security_score": security_score,
        "cost_score": cost_score,
        "reasons": reasons,
    }
