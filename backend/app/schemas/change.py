from pydantic import BaseModel
from typing import Optional


class Change(BaseModel):
    source: str
    resource_type: Optional[str] = None
    resource_name: Optional[str] = None
    attribute: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class ChangeAnalysisRequest(BaseModel):
    changed_files: list[str]
    diffs: dict[str, str]
