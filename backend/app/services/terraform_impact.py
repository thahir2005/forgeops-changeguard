INSTANCE_SIZE_ORDER = {
    "t3.nano": 1,
    "t3.micro": 2,
    "t3.small": 3,
    "t3.medium": 4,
    "t3.large": 5,
    "t3.xlarge": 6,
    "t3.2xlarge": 7,
}


def analyze_terraform_impact(change: dict) -> dict:
    """
    Determine the potential impact of a Terraform change.
    """

    resource_type = change.get("resource_type")
    attribute = change.get("attribute")
    old_value = change.get("old_value")
    new_value = change.get("new_value")

    impact = {
        "cost": "low",
        "reliability": "low",
        "security": "low",
        "capacity": "low",
        "reasons": [],
    }

    # EC2 instance size change
    if (
        resource_type == "aws_instance"
        and attribute == "instance_type"
    ):

        old_rank = INSTANCE_SIZE_ORDER.get(old_value)
        new_rank = INSTANCE_SIZE_ORDER.get(new_value)

        if old_rank and new_rank:

            if new_rank > old_rank:
                impact["cost"] = "high"
                impact["capacity"] = "high"

                impact["reasons"].append(
                    f"Compute capacity increases from "
                    f"{old_value} to {new_value}."
                )

                impact["reasons"].append(
                    "The larger instance type may increase "
                    "monthly cloud infrastructure cost."
                )

            elif new_rank < old_rank:
                impact["cost"] = "medium"
                impact["capacity"] = "medium"

                impact["reasons"].append(
                    f"Compute capacity decreases from "
                    f"{old_value} to {new_value}."
                )

                impact["reasons"].append(
                    "Reduced capacity may increase performance "
                    "or resource-exhaustion risk."
                )

    return impact
