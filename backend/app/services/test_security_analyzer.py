from app.services.security_analyzer import analyze_security_change


security_diff = """
--- a/infrastructure/terraform/security.tf
+++ b/infrastructure/terraform/security.tf
@@ -10,7 +10,7 @@
 resource "aws_security_group_rule" "api" {
-  cidr_blocks = ["10.0.0.0/16"]
+  cidr_blocks = ["0.0.0.0/0"]
 }
"""


findings = analyze_security_change(
    security_diff
)


print("ForgeOps Security Analysis")
print("==========================")

for finding in findings:
    print(finding)
