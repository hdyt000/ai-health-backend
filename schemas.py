from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal


class LabParameter(BaseModel):
    name: str
    value: Union[float, str]
    unit: Optional[str] = None
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None


class LabRequest(BaseModel):
    gender: Optional[str] = Field(None, description="male / female")
    age: Optional[int] = Field(None, description="Age")
    raw_text: str = Field(..., description="Raw lab text")


class AnalysisExplanation(BaseModel):
    summary: str
    recommendation: str


class PatternMatch(BaseModel):
    code: str
    title: str
    severity: Literal["low", "medium", "high"]
    evidence: List[str]


class RiskResult(BaseModel):
    score: int
    risk_level: Literal["low", "medium", "high"]
    abnormal_parameters: List[str]
    patterns: List[PatternMatch]


class LabResponse(BaseModel):
    detected_language: str
    parsed_parameters: List[LabParameter]
    risk: RiskResult
    analysis: AnalysisExplanation