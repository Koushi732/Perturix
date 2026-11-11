from pydantic import BaseModel


class EvaluationEntity(BaseModel):
    evaluation_id: str
    job_id: str
    psnr: float
    ssim: float
    lpips: float
    mse: float
    file_size_diff_kb: float
    protection_score: float
