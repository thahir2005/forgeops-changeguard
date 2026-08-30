from fastapi import APIRouter

from app.schemas.change import PullRequestAnalysisRequest
from app.services.pr_analysis_service import PRAnalysisService


router = APIRouter(
    prefix="/api/v1/pull-requests",
    tags=["Pull Requests"],
)


@router.post("/analyze")
def analyze_pull_request_endpoint(
    request: PullRequestAnalysisRequest,
):
    """
    Analyze a GitHub pull request using
    ForgeOps ChangeGuard.
    """

    service = PRAnalysisService()

    return service.analyze_pull_request(
        owner=request.owner,
        repo=request.repo,
        pull_number=request.pull_number,
    )
