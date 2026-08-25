from pprint import pprint

from app.services.change_service import analyze_change


changed_files = [
    "infrastructure/terraform/main.tf",
    "infrastructure/kubernetes/deployment.yaml",
]


terraform_diff = """
--- a/infrastructure/terraform/main.tf
+++ b/infrastructure/terraform/main.tf
@@ -10,7 +10,7 @@
 resource "aws_instance" "app" {
-  instance_type = "t3.medium"
+  instance_type = "t3.2xlarge"
 }
"""


kubernetes_diff = """
--- a/infrastructure/kubernetes/deployment.yaml
+++ b/infrastructure/kubernetes/deployment.yaml
@@ -10,7 +10,7 @@
 spec:
-  replicas: 3
+  replicas: 1
"""


diffs = {
    "infrastructure/terraform/main.tf": terraform_diff,
    "infrastructure/kubernetes/deployment.yaml": kubernetes_diff,
}


result = analyze_change(
    changed_files,
    diffs,
)


print("\nForgeOps End-to-End Analysis")
print("============================")

pprint(result)
