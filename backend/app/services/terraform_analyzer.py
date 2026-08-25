import re


def analyze_terraform_change(
    diff_text: str,
) -> list[dict]:
    """
    Extract basic infrastructure changes from a Terraform diff.
    """

    changes = []

    resource_match = re.search(
        r'resource\s+"([^"]+)"\s+"([^"]+)"',
        diff_text,
    )

    resource_type = None
    resource_name = None

    if resource_match:
        resource_type = resource_match.group(1)
        resource_name = resource_match.group(2)

    added_lines = []
    removed_lines = []

    for line in diff_text.splitlines():

        if line.startswith("+++") or line.startswith("---"):
            continue

        if line.startswith("+"):
            added_lines.append(line[1:].strip())

        elif line.startswith("-"):
            removed_lines.append(line[1:].strip())

    for removed in removed_lines:

        match = re.match(
            r'(\w+)\s*=\s*"([^"]*)"',
            removed,
        )

        if not match:
            continue

        attribute = match.group(1)
        old_value = match.group(2)

        for added in added_lines:

            added_match = re.match(
                rf'{re.escape(attribute)}\s*=\s*"([^"]*)"',
                added,
            )

            if added_match:
                new_value = added_match.group(1)

                changes.append(
                    {
                        "resource_type": resource_type,
                        "resource_name": resource_name,
                        "attribute": attribute,
                        "old_value": old_value,
                        "new_value": new_value,
                    }
                )

    return changes
