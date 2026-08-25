from app.services.kubernetes_analyzer import analyze_kubernetes_change


kubernetes_diff = """
--- a/infrastructure/kubernetes/deployment.yaml
+++ b/infrastructure/kubernetes/deployment.yaml
@@ -10,12 +10,12 @@
 spec:
-  replicas: 3
+  replicas: 1

 containers:
   - name: payment-api
-    image: payment-api:v1.4
+    image: payment-api:v1.5

     resources:
       limits:
-        memory: "2Gi"
+        memory: "512Mi"
-        cpu: "500m"
+        cpu: "100m"
"""


changes = analyze_kubernetes_change(kubernetes_diff)


print("Kubernetes Changes")
print("==================")

for change in changes:
    print(change)
