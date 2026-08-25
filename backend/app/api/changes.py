from fastapi import APIRouter

from app.schemas.change import ChangeAnalysisRequest
from app.services.change_service import analyze_change


router = APIRouter(
    prefix="/api/v1/changes",
    tags=["Changes"],
)


@router.post("/analyze")
def analyze_change_endpoint(
    request: ChangeAnalysisRequest,
):
    """
    Analyze a proposed infrastructure/application change.
    """

    result = analyze_change(
        changed_files=request.changed_files,
        diffs=request.diffs,
    )

    return result
