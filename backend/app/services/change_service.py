from app.services.diff_analyzer import analyze_diff
from app.services.terraform_analyzer import analyze_terraform_change
from app.services.terraform_impact import analyze_terraform_impact
from app.services.kubernetes_analyzer import analyze_kubernetes_change
from app.services.kubernetes_impact import analyze_kubernetes_impact
from app.services.security_analyzer import analyze_security_change
from app.services.risk_engine import calculate_overall_risk


def analyze_change(
    changed_files: list[str],
    diffs: dict[str, str],
    directly_affected_services: list[str] | None = None,
    transitively_affected_services: list[str] | None = None,
) -> dict:
    """
    Run the complete ForgeOps change analysis pipeline.
    """

    terraform_impacts = []
    kubernetes_impacts = []
    security_findings = []

    analyzed_files = []

    # -------------------------------------------------
    # Analyze each changed file
    # -------------------------------------------------

    for file_path in changed_files:

        diff_text = diffs.get(
            file_path,
            "",
        )

        diff_result = analyze_diff(
            file_path,
            diff_text,
        )

        analyzed_files.append(
            {
                "file": file_path,
                "change_type": diff_result.change_type,
                "added_lines": diff_result.added_lines,
                "removed_lines": diff_result.removed_lines,
            }
        )

        # ---------------------------------------------
        # Terraform
        # ---------------------------------------------

        if file_path.endswith(".tf"):

            terraform_changes = (
                analyze_terraform_change(
                    diff_text
                )
            )

            for change in terraform_changes:

                impact = analyze_terraform_impact(
                    change
                )

                terraform_impacts.append(
                    impact
                )

        # ---------------------------------------------
        # Kubernetes
        # ---------------------------------------------

        if (
            file_path.endswith(".yaml")
            or file_path.endswith(".yml")
        ):

            kubernetes_changes = (
                analyze_kubernetes_change(
                    diff_text
                )
            )

            for change in kubernetes_changes:

                impact = analyze_kubernetes_impact(
                    change
                )

                kubernetes_impacts.append(
                    impact
                )

        # ---------------------------------------------
        # Security
        # ---------------------------------------------

        findings = analyze_security_change(
            diff_text
        )

        security_findings.extend(
            findings
        )

    # -------------------------------------------------
    # Unified risk
    # -------------------------------------------------

    risk = calculate_overall_risk(
        terraform_impacts=terraform_impacts,
        kubernetes_impacts=kubernetes_impacts,
        security_findings=security_findings,
        directly_affected_services=(
            directly_affected_services
            or []
        ),
        transitively_affected_services=(
            transitively_affected_services
            or []
        ),
    )

    return {
        "files_changed": len(changed_files),
        "files": analyzed_files,
        "terraform_impacts": terraform_impacts,
        "kubernetes_impacts": kubernetes_impacts,
        "security_findings": security_findings,
        "risk": risk,
    }
