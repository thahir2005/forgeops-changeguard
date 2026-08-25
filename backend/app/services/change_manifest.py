from app.schemas.change import Change


def build_change_manifest(
    terraform_changes: list[dict],
    kubernetes_changes: list[dict],
) -> list[Change]:
    """
    Combine changes from different analyzers
    into one unified change model.
    """

    manifest = []

    # Terraform changes
    for change in terraform_changes:

        manifest.append(
            Change(
                source="terraform",
                resource_type=change.get("resource_type"),
                resource_name=change.get("resource_name"),
                attribute=change.get("attribute"),
                old_value=str(change.get("old_value")),
                new_value=str(change.get("new_value")),
            )
        )

    # Kubernetes changes
    for change in kubernetes_changes:

        manifest.append(
            Change(
                source="kubernetes",
                resource_type=change.get("resource"),
                resource_name=None,
                attribute=change.get("attribute"),
                old_value=str(change.get("old_value")),
                new_value=str(change.get("new_value")),
            )
        )

    return manifest
