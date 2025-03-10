import os
import uuid
from dotenv import load_dotenv
from pathlib import Path
from typing import List
from fastapi import FastAPI, UploadFile
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from server import PipelineManager


load_dotenv()
KFP_URL = os.getenv("KFP_URL")
ENABLE_CACHING = bool(os.getenv("ENABLE_CACHING"))
INTERVAL = int(os.getenv("INTERVAL"))
PIPELINES_DIR = os.getenv("PIPELINES_DIR")

pipelines_dir = Path(PIPELINES_DIR)
pipelines_dir = pipelines_dir.resolve()
pipelines_dir.mkdir(parents=True, exist_ok=True)

pmanager = PipelineManager(KFP_URL, ENABLE_CACHING, pipelines_dir)
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        func=pmanager.process_pipelines,
        trigger="interval",
        seconds=INTERVAL,
    )
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def handle_root():
    return {
        "status": "success",
        "message": "ML pipeline placement system",
    }


@app.post("/submit/")
async def upload_file(components: List[UploadFile], pipeline: UploadFile):
    pipeline_id = str(uuid.uuid4())
    path = pipelines_dir / pipeline_id
    path.mkdir(parents=True, exist_ok=True)
    
    # Save component files
    filenames = []
    for file in components:
        print(file.filename)
        filenames.append(file.filename)
        content = await file.read()
        with open(path / file.filename, "wb") as f:
            f.write(content)

    # Save pipeline file
    filenames.append(pipeline.filename)
    with open(path / pipeline.filename, "wb") as f:
        content = await pipeline.read()
        f.write(content)

    # Add pipeline to the queue
    pmanager.add_pipeline(pipeline_id)

    response = {
        "status": "success",
        "message": "Pipeline submitted successfully",
        "pipeline_id": pipeline_id,
        "files": filenames,
    }
    return response
    