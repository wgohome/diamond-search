import csv
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


class DiamondResultRow(BaseModel):
    target: str
    p_identity: float
    algn_length: int
    mismatches: int
    gap_openings: int
    e_value: str
    bit_score: float


class ProteinResult(BaseModel):
    job_id: str
    status: QueryStatus
    result: list | None = None

    @classmethod
    def retrieve(cls, job_id: str, with_data: bool = True) -> "ProteinResult":
        filepath = settings.protein_result_filepath(job_id)
        if os.path.exists(filepath):
            return cls(
                job_id=job_id,
                status=QueryStatus.COMPLETED,
                result=cls._parse_result(filepath) if with_data else None
            )
        else:
            return cls(
                job_id=job_id,
                status=QueryStatus.PROCESSING,
            )

    @classmethod
    def _parse_result(cls, filepath: str) -> list[DiamondResultRow]:
        reader = csv.reader(
            open(filepath, "r"),
            delimiter="\t",
            quotechar="'"
        )
        results = [
            DiamondResultRow(
                target=row[1],
                p_identity=float(row[2]),
                algn_length=int(row[3]),
                mismatches=int(row[4]),
                gap_openings=int(row[5]),
                e_value=row[10],
                bit_score=float(row[11]),
            )
            for row in reader
        ]
        return results
