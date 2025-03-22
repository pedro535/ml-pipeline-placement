import uuid
from typing import List
from fastapi import FastAPI, UploadFile
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from server import PipelineManager, PlacementDecisionUnit, NodeManager, DataManager
from server.settings import (
    WAIT_INTERVAL,
    UPDATE_INTERVAL,
    METADATA_FILENAME,
    PIPELINE_FILENAME,
    pipelines_dir
)


nmanager = NodeManager()
pdunit = PlacementDecisionUnit(nmanager)
pmanager = PipelineManager(pdunit)
dmanager = DataManager()
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        func=pmanager.process_pipelines,
        trigger="interval",
        seconds=WAIT_INTERVAL,
    )
    scheduler.add_job(
        func=pmanager.update_running_pipeline,
        trigger="interval",
        seconds=UPDATE_INTERVAL,
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
async def upload_file(
    components: List[UploadFile],
    pipeline: UploadFile,
    metadata: UploadFile
):
    pipeline_id = str(uuid.uuid4())
    path = pipelines_dir / pipeline_id
    path.mkdir(parents=True, exist_ok=True)
    
    # Save component files
    component_files = []
    for file in components:
        component_files.append(file.filename)
        content = await file.read()
        with open(path / file.filename, "wb") as f:
            f.write(content)

    # Save pipeline file
    with open(path / PIPELINE_FILENAME, "wb") as f:
        content = await pipeline.read()
        f.write(content)

    # Save metadata file
    with open(path / METADATA_FILENAME, "wb") as f:
        content = await metadata.read()
        f.write(content)

    # Register pipeline
    pmanager.add_pipeline(
        pipeline_id=pipeline_id,
        component_files=component_files
    )

    response = {
        "status": "success",
        "message": "Pipeline submitted successfully",
        "pipeline_id": pipeline_id
    }
    return response
    