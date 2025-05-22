from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class JobListItem(BaseModel):
    job_id: UUID
    query: str
    status: str
    created_at: datetime

class JobDetail(BaseModel):
    job_id: UUID
    query: str
    domain: Optional[str]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    result_count: int 