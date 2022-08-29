from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
)
from fastapi.responses import RedirectResponse
import datetime
import os
import uuid

from models import ProteinQuery, QueryResponse, ProteinResult
from config import settings

app = FastAPI(
    title="Plant Protein Search"
)


def create_job_id() -> str:
    # `job_id` twofold role here:
    #   - Unique identifier of query jobs to be queued, and have results retrieved
    #   - Extract timestamp information, to determine expiry of job
    return str(uuid.uuid1())

def get_datetime_from_uuid1(job_id: uuid.UUID) -> datetime.datetime:
    return datetime.datetime(1582, 10, 15) + datetime.timedelta(microseconds=job_id.time // 10)


def protein_seq_valid(protein_seq: str) -> bool:
    aa_letters = set("ARNDCQEGHILKMFPSTWYV")
    return set(protein_seq.upper()) - aa_letters == set()


def run_diamond_blastp(protein_seq: str, job_id: str) -> None:
    with open(settings.protein_query_filepath(job_id), "w") as file:
        file.write(f">{job_id}\n{protein_seq}\n")
    # run diamond search
    # TODO
    return None


@app.get("/")
def redirect_to_docs():
    return RedirectResponse("/docs")


@app.post("/queries/proteins", response_model=QueryResponse)
async def protein_query(background_tasks: BackgroundTasks, body: ProteinQuery):
    protein_seq = body.protein_seq
    if protein_seq_valid(protein_seq) is False:
        raise HTTPException(
            status_code=400,
            detail="Protein sequence queried found to be invalid. Enter only valid amino acid letters."
        )
    job_id = create_job_id()
    background_tasks.add_task(
        run_diamond_blastp,
        protein_seq=protein_seq,
        job_id = job_id
    )
    return QueryResponse(job_id=job_id)


@app.get(
    "/results/proteins",
    response_model=list[ProteinResult],
    response_model_exclude_none=True
)
async def get_results_index():
    # TODO: paginate?
    results = [
        ProteinResult.retrieve(settings.protein_query_job_id(filename), with_data=False)
        for filename in os.listdir(settings.PROTEIN_QUERIES_DIR)
        if filename.endswith(settings.PROTEIN_QUERIES_SUFFIX)
    ]
    return results


@app.get("/results/proteins/{job_id}", response_model=ProteinResult)
async def get_result(job_id: str):
    if not os.path.exists(settings.protein_query_filepath(job_id)):
        return HTTPException(
            status_code=400,
            detail="Invalid job_id. It may have expired or is not in the system.",
        )
    return ProteinResult.retrieve(job_id)
