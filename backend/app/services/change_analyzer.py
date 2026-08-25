from pathlib import Path


def classify_file(file_path: str) -> str:
    """
    Classify a changed file according to its role
    in a cloud-native application.
    """

    path = Path(file_path)
    name = path.name.lower()
    suffix = path.suffix.lower()

    # Infrastructure as Code
    if suffix == ".tf":
        return "terraform"

    # Kubernetes
    if (
        "kubernetes" in path.parts
        or name.endswith((".yaml", ".yml"))
        and any(
            keyword in name
            for keyword in [
                "deployment",
                "service",
                "ingress",
                "configmap",
                "secret",
            ]
        )
    ):
        return "kubernetes"

    # Docker
    if name == "dockerfile" or name.startswith("dockerfile."):
        return "docker"

    # Security-sensitive files
    if (
        ".env" in name
        or "secret" in name
        or "credential" in name
        or "iam" in name
    ):
        return "security"

    # Python application
    if suffix == ".py":
        return "application"

    # JavaScript / TypeScript
    if suffix in {".js", ".jsx", ".ts", ".tsx"}:
        return "application"

    # Configuration
    if suffix in {".json", ".yaml", ".yml", ".toml"}:
        return "configuration"

    return "other"


def analyze_changes(changed_files: list[str]) -> dict:
    """
    Analyze a collection of changed files.
    """

    changes = []

    for file_path in changed_files:
        changes.append(
            {
                "file": file_path,
                "category": classify_file(file_path),
            }
        )

    categories = {}

    for change in changes:
        category = change["category"]
        categories[category] = categories.get(category, 0) + 1

    return {
        "total_files": len(changed_files),
        "categories": categories,
        "changes": changes,
    }
