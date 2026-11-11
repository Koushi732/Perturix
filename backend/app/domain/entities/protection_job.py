
from pydantic import BaseModel


class ProtectionJobEntity(BaseModel):
    job_id: str
    original_file_id: str
    algorithm: str
    epsilon: float
    status: str
    time_taken_ms: int | None = None
    protected_file_id: str | None = None
