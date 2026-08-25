from app.services.terraform_analyzer import analyze_terraform_change


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


changes = analyze_terraform_change(terraform_diff)


for change in changes:
    print(change)
