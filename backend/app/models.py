from pydantic import BaseModel, Field


class PatientSample(BaseModel):
    cnv_aberration_score: float = Field(..., ge=0.0, le=10.0, description="CNV-derived aberration magnitude")
    methylation_score: float = Field(..., ge=0.0, le=10.0, description="Methylation signal score")
    fragment_size_entropy: float = Field(..., ge=0.0, le=5.0, description="Fragmentation entropy from cfDNA")
    tumor_fraction: float = Field(..., ge=0.0, le=1.0, description="Estimated tumor fraction in cfDNA")
    age: int = Field(..., ge=18, le=100, description="Patient age")
    smoking_history: bool = Field(..., description="Smoking history present")
    prior_cancer: bool = Field(..., description="Prior cancer diagnosis")


class PredictionResult(BaseModel):
    malignancy_risk: float = Field(..., ge=0.0, le=1.0)
    survival_risk: float = Field(..., ge=0.0, le=1.0)
    predicted_stage: str
    explanation: str
