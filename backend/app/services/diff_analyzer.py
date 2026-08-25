from dataclasses import dataclass


@dataclass
class DiffChange:
    file: str
    change_type: str
    added_lines: list[str]
    removed_lines: list[str]


def analyze_diff(
    file_path: str,
    diff_text: str,
) -> DiffChange:
    """
    Analyze a unified Git diff for one file.
    """

    added_lines = []
    removed_lines = []

    for line in diff_text.splitlines():

        # Ignore Git metadata lines
        if line.startswith("+++") or line.startswith("---"):
            continue

        if line.startswith("+"):
            added_lines.append(line[1:])

        elif line.startswith("-"):
            removed_lines.append(line[1:])

    if added_lines and removed_lines:
        change_type = "modified"

    elif added_lines:
        change_type = "added"

    elif removed_lines:
        change_type = "removed"

    else:
        change_type = "unchanged"

    return DiffChange(
        file=file_path,
        change_type=change_type,
        added_lines=added_lines,
        removed_lines=removed_lines,
    )
