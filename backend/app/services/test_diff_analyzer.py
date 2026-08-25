from app.services.diff_analyzer import analyze_diff


terraform_diff = """
--- a/infrastructure/terraform/main.tf
+++ b/infrastructure/terraform/main.tf
@@ -10,7 +10,7 @@
 resource "aws_instance" "app" {
-  instance_type = "t3.medium"
+  instance_type = "t3.2xlarge"
   ami           = "ami-123456"
 }
"""


result = analyze_diff(
    "infrastructure/terraform/main.tf",
    terraform_diff,
)

print("File:", result.file)
print("Change type:", result.change_type)
print("Added lines:", result.added_lines)
print("Removed lines:", result.removed_lines)
