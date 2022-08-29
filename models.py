from enum import Enum
import os
from pydantic import (
    BaseModel,
    validator,
)

from config import settings


class QueryStatus(Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"


class ProteinQuery(BaseModel):
    protein_seq: str

    @validator("protein_seq")
    def upcase_protein(cls, v):
        return v.upper()


class QueryResponse(BaseModel):
    job_id: str


class QueryResult(BaseModel):
    job_id: str
    status: QueryStatus
    result: list | None = None

    @classmethod
    def retrieve(cls, job_id):
        results_filepath = settings.protein_result_filepath(job_id)
        # TODO: open results and parse
        # Paginate?
        if os.path.exists(results_filepath):
            return cls(
                job_id=job_id,
                status=QueryStatus.COMPLETED,
                result=[]
            )
        else:
            return cls(
                job_id=job_id,
                status=QueryStatus.PROCESSING,
            )
