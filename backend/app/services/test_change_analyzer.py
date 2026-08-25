from app.services.change_analyzer import analyze_changes


files = [
    "backend/app/main.py",
    "infrastructure/terraform/main.tf",
    "infrastructure/kubernetes/deployment.yaml",
    "Dockerfile",
    ".env.example",
    "frontend/src/App.jsx",
]

result = analyze_changes(files)

print(result)

files = [
    "backend/app/main.py",
    "infrastructure/terraform/main.tf",
    "infrastructure/kubernetes/deployment.yaml",
    "Dockerfile",
    ".env.example",
    "frontend/src/App.jsx",
]

result = analyze_changes(files)

print(result)
