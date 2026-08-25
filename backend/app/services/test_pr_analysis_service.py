from pprint import pprint

from app.services.pr_analysis_service import (
    PRAnalysisService,
)


OWNER = "thahir2005"
REPO = "forgeops-changeguard-demo"
PR_NUMBER = 1


def main():

    service = PRAnalysisService()

    print()
    print("ForgeOps Pull Request Analysis")
    print("==============================")
    print()

    result = service.analyze_pull_request(
        owner=OWNER,
        repo=REPO,
        pull_number=PR_NUMBER,
    )

    pr = result["pull_request"]
    analysis = result["analysis"]

    print("Repository:")
    print(result["repository"])

    print()
    print("Pull Request:")
    print(f"#{pr['number']} - {pr['title']}")

    print()
    print("Author:")
    print(pr["author"])

    print()
    print("Branches:")
    print(
        f"{pr['head_branch']} → "
        f"{pr['base_branch']}"
    )

    print()
    print("Changed Files:")
    print(
        analysis["files_changed"]
    )

    for file in analysis["files"]:
        print(
            f"- {file['file']} "
            f"({file['change_type']})"
        )

    print()
    print("Risk Assessment")
    print("================")

    risk = analysis["risk"]

    print(
        f"Overall Score: "
        f"{risk['overall_score']}"
    )

    print(
        f"Category: "
        f"{risk['category']}"
    )

    print(
        f"Reliability: "
        f"{risk['reliability_score']}"
    )

    print(
        f"Security: "
        f"{risk['security_score']}"
    )

    print(
        f"Cost: "
        f"{risk['cost_score']}"
    )

    print()
    print("Reasons:")

    for reason in risk["reasons"]:
        print(f"- {reason}")


if __name__ == "__main__":
    main()
