from pydantic import BaseModel, Field
from typing import List

class Plan(BaseModel):
    intent: str
    steps: List[str] = Field(default_factory=list)
    expected_rules: List[str] = Field(default_factory=list)

class PatchOut(BaseModel):
    patch_unified: str
    rationale: str
    touched_files: List[str] = Field(default_factory=list)
