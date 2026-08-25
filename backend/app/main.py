from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.changes import router as changes_router


app = FastAPI(
    title="ForgeOps ChangeGuard",
    description="AI-assisted cloud change intelligence platform",
    version="0.1.0",
)


# Allow the React development server to communicate
# with the FastAPI backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(changes_router)


@app.get("/")
def root():
    return {
        "name": "ForgeOps ChangeGuard",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
