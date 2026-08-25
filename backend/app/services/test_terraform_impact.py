from app.services.terraform_impact import analyze_terraform_impact


change = {
    "resource_type": "aws_instance",
    "resource_name": "app",
    "attribute": "instance_type",
    "old_value": "t3.medium",
    "new_value": "t3.2xlarge",
}


impact = analyze_terraform_impact(change)

print("Terraform Change Impact")
print("=======================")

print("Cost:", impact["cost"])
print("Reliability:", impact["reliability"])
print("Security:", impact["security"])
print("Capacity:", impact["capacity"])

print("\nReasons:")

for reason in impact["reasons"]:
    print("-", reason)
