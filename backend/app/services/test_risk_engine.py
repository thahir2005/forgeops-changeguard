from app.services.risk_engine import calculate_overall_risk


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
