from app.services.change_manifest import build_change_manifest


terraform_changes = [
    {
        "resource_type": "aws_instance",
        "resource_name": "app",
        "attribute": "instance_type",
        "old_value": "t3.medium",
        "new_value": "t3.2xlarge",
    }
]


kubernetes_changes = [
    {
        "resource": "deployment",
        "attribute": "replicas",
        "old_value": 3,
        "new_value": 1,
    }
]


manifest = build_change_manifest(
    terraform_changes,
    kubernetes_changes,
)


print("Unified Change Manifest")
print("=======================")

for change in manifest:
    print(change.model_dump())
