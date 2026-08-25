import re


def analyze_kubernetes_change(diff_text: str) -> list[dict]:
    """
    Extract important Kubernetes workload changes
    from a unified Git diff.
    """

    changes = []

    # Detect replicas
    replica_pattern = re.compile(
        r"[-+]\s*replicas:\s*(\d+)"
    )

    replica_values = replica_pattern.findall(diff_text)

    if len(replica_values) >= 2:
        old_value = int(replica_values[0])
        new_value = int(replica_values[1])

        changes.append(
            {
                "resource": "deployment",
                "attribute": "replicas",
                "old_value": old_value,
                "new_value": new_value,
            }
        )

    # Detect memory limits
    memory_pattern = re.compile(
        r'[-+]\s*memory:\s*"([^"]+)"'
    )

    memory_values = memory_pattern.findall(diff_text)

    if len(memory_values) >= 2:
        changes.append(
            {
                "resource": "container",
                "attribute": "memory_limit",
                "old_value": memory_values[0],
                "new_value": memory_values[1],
            }
        )

    # Detect CPU limits
    cpu_pattern = re.compile(
        r'[-+]\s*cpu:\s*"([^"]+)"'
    )

    cpu_values = cpu_pattern.findall(diff_text)

    if len(cpu_values) >= 2:
        changes.append(
            {
                "resource": "container",
                "attribute": "cpu_limit",
                "old_value": cpu_values[0],
                "new_value": cpu_values[1],
            }
        )

    # Detect container image
    image_pattern = re.compile(
        r'[-+]\s*image:\s*([^\s]+)'
    )

    image_values = image_pattern.findall(diff_text)

    if len(image_values) >= 2:
        changes.append(
            {
                "resource": "container",
                "attribute": "image",
                "old_value": image_values[0],
                "new_value": image_values[1],
            }
        )

    return changes
