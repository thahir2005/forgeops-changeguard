from app.services.risk_engine import (
    calculate_blast_radius_score,
    calculate_overall_risk,
)

# -------------------------------------------------
# Blast radius scoring
# -------------------------------------------------

assert calculate_blast_radius_score(0, 0) == 0
assert calculate_blast_radius_score(1, 0) == 20
assert calculate_blast_radius_score(1, 1) == 50
assert calculate_blast_radius_score(2, 2) == 70
assert calculate_blast_radius_score(3, 3) == 100


terraform_impacts = [
    {
        "cost": "high",
        "reliability": "low",
        "security": "low",
        "reasons": [
            "EC2 instance size increased.",
            "Monthly infrastructure cost may increase.",
        ],
    }
]


kubernetes_impacts = [
    {
        "cost": "low",
        "reliability": "high",
        "security": "low",
        "reasons": [
            "Replica count decreased from 3 to 1.",
            "Application redundancy is reduced.",
        ],
    }
]


security_findings = [
    {
        "type": "public_network_exposure",
        "severity": "critical",
        "message": (
            "Resource may be exposed "
            "to the public internet."
        ),
    }
]


result = calculate_overall_risk(
    terraform_impacts,
    kubernetes_impacts,
    security_findings,
)


# -------------------------------------------------
# Expected scores
# -------------------------------------------------

assert result["reliability_score"] == 80
assert result["security_score"] == 100
assert result["cost_score"] == 80

# 80 * 0.4 + 100 * 0.3 + 80 * 0.3 = 86
assert result["overall_score"] == 86

assert result["category"] == "critical"


# -------------------------------------------------
# Expected reasons
# -------------------------------------------------

assert (
    "EC2 instance size increased."
    in result["reasons"]
)

assert (
    "Replica count decreased from 3 to 1."
    in result["reasons"]
)

assert (
    "Resource may be exposed "
    "to the public internet."
    in result["reasons"]
)

# -------------------------------------------------
# Blast radius integration
# -------------------------------------------------

blast_radius_result = calculate_overall_risk(
    terraform_impacts=[],
    kubernetes_impacts=[],
    security_findings=[],
    directly_affected_services=[
        "payment-api",
        "checkout-service",
    ],
    transitively_affected_services=[
        "order-service",
    ],
)
assert blast_radius_result["blast_radius_score"] == 50
assert blast_radius_result["reliability_score"] == 50
assert blast_radius_result["security_score"] == 0
assert blast_radius_result["cost_score"] == 0

# 70 * 0.4 = 28
assert blast_radius_result["overall_score"] == 20
assert blast_radius_result["category"] == "low"

assert (
    "Dependency blast radius affects 3 service(s)."
    in blast_radius_result["reasons"]
)

assert (
    "Direct dependency impact affects 2 service(s)."
    in blast_radius_result["reasons"]
)

assert (
    "Transitive dependency impact indicates "
    "potential cascading operational effects."
    in blast_radius_result["reasons"]
)


print("ForgeOps Unified Risk Assessment")
print("================================")

print("Overall Score:", result["overall_score"])
print("Risk Category:", result["category"])

print("Reliability:", result["reliability_score"])
print("Security:", result["security_score"])
print("Cost:", result["cost_score"])

print("\nReasons:")

for reason in result["reasons"]:
    print("-", reason)

print("\nAll risk engine assertions passed.")