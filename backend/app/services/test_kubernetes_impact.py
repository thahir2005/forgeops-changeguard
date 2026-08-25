from app.services.kubernetes_impact import analyze_kubernetes_impact


change = {
    "resource": "deployment",
    "attribute": "replicas",
    "old_value": 3,
    "new_value": 1,
}


impact = analyze_kubernetes_impact(change)


print("Kubernetes Change Impact")
print("=======================")

print("Reliability:", impact["reliability"])
print("Cost:", impact["cost"])
print("Performance:", impact["performance"])
print("Deployment:", impact["deployment"])

print("\nReasons:")

for reason in impact["reasons"]:
    print("-", reason)
