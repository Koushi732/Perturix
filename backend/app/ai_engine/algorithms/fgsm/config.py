from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FGSMConfig(BaseModel):
    name: str = Field(default="FGSM", description="Name of the attack algorithm")
    version: str = Field(default="1.0", description="Version of the attack algorithm")
    epsilon: float = Field(default=8.0, gt=0.0, description="Perturbation magnitude")
    clamp_min: float = Field(default=0.0, description="Minimum allowed pixel value")
    clamp_max: float = Field(default=255.0, description="Maximum allowed pixel value")
    
    model_config = ConfigDict(frozen=True)

    @model_validator(mode='after')
    def validate_clamps(self) -> Self:
        if self.clamp_min >= self.clamp_max:
            raise ValueError("clamp_min must be strictly less than clamp_max")
        return self
