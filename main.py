import random
import time
from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
)
from fastapi.responses import RedirectResponse
import datetime
import os
import uuid

from models import ProteinQuery, QueryResponse, ProteinResult, QueryStatus
from config import settings

app = FastAPI(
    title="Plant Protein Search"
)


@app.on_event("startup")
async def startup_event():
    os.makedirs(settings.PROTEIN_QUERIES_DIR, exist_ok=True)
    os.makedirs(settings.PROTEIN_RESULTS_DIR, exist_ok=True)
    if not os.path.isfile("diamond") or not os.path.isfile("plants_all.dmnd"):
        os.system("sh run_setup.sh")


def create_job_id() -> str:
    # `job_id` twofold role here:
    #   - Unique identifier of query jobs to be queued, and have results retrieved
    #   - Extract timestamp information, to determine expiry of job
    return str(uuid.uuid1())


def get_datetime_from_uuid1(job_uuid: uuid.UUID) -> datetime.datetime:
    return datetime.datetime(1582, 10, 15) + datetime.timedelta(microseconds=job_uuid.time // 10)


def make_uuid1_from_datetime(given_dt: datetime.datetime) -> uuid.UUID:
    timestamp = given_dt.timestamp()
    nanoseconds = int(timestamp * 1e9)
    # 0x01b21dd213814000 is the number of 100-ns intervals between the
    # UUID epoch 1582-10-15 00:00:00 and the Unix epoch 1970-01-01 00:00:00.
    timestamp = int(nanoseconds//100) + 0x01b21dd213814000
    time_low = timestamp & 0xffffffff
    time_mid = (timestamp >> 32) & 0xffff
    time_hi_version = (timestamp >> 48) & 0x0fff
    clock_seq = random.randrange(1<<14)
    clock_seq_low = clock_seq & 0xff
    clock_seq_hi_variant = (clock_seq >> 8) & 0x3f
    return uuid.UUID(fields=(time_low, time_mid, time_hi_version, clock_seq_low, clock_seq_hi_variant, uuid.getnode()))


def protein_seq_valid(protein_seq: str) -> bool:
    aa_letters = set("ARNDCQEGHILKMFPSTWYV")
    return set(protein_seq.upper()) - aa_letters == set()


def run_diamond_blastp(protein_seq: str, job_id: str) -> None:
    # Write query
    with open(settings.protein_query_filepath(job_id), "w") as file:
        file.write(f">{job_id}\n{protein_seq}\n")
    # Run query
    os.system(f"./diamond blastp -q {settings.protein_query_filepath(job_id)} -o {settings.protein_result_filepath(job_id)} -d {settings.DIAMOND_DB_NAME}")
    return None


def delete_query_and_results() -> None:
    job_ids = [
        settings.protein_query_job_id(filename)
        for filename in os.listdir(settings.PROTEIN_QUERIES_DIR)
        if filename.endswith(settings.PROTEIN_QUERIES_SUFFIX)
    ]
    expired_job_ids = [
        job_id
        for job_id in job_ids
        if get_datetime_from_uuid1(uuid.UUID(job_id)) < (datetime.datetime.now() - datetime.timedelta(days=settings.DAYS_DELETE_QUERY))
    ]
    for job_id in expired_job_ids:
        query_filepath = settings.protein_query_filepath(job_id)
        result_filepath = settings.protein_result_filepath(job_id)
        os.remove(query_filepath)
        if os.path.isfile(result_filepath):
            os.remove(result_filepath)


@app.get("/")
def redirect_to_docs():
    if not os.path.isfile("diamond"):
        os.system("sh run_setup.sh")
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
    background_tasks.add_task(delete_query_and_results)
    return QueryResponse(job_id=job_id)


# To wait for the search to be done and return the results
@app.post("/queries/proteins/wait", response_model=ProteinResult)
async def protein_query_with_wait(background_tasks: BackgroundTasks, body: ProteinQuery):
    protein_seq = body.protein_seq
    if protein_seq_valid(protein_seq) is False:
        raise HTTPException(
            status_code=400,
            detail="Protein sequence queried found to be invalid. Enter only valid amino acid letters."
        )
    job_id = create_job_id()
    run_diamond_blastp(protein_seq=protein_seq, job_id=job_id)
    result = ProteinResult.retrieve(job_id)
    background_tasks.add_task(delete_query_and_results)
    while result.status != QueryStatus.COMPLETED:
        time.sleep(3)
        result = ProteinResult.retrieve(job_id)
    return result


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
