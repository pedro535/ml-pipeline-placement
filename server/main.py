import uuid
from typing import List
from fastapi import FastAPI, UploadFile
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from server import PipelineManager, DecisionUnit, NodeManager, DataManager
from server.settings import (
    WAIT_INTERVAL,
    UPDATE_INTERVAL,
    METADATA_FILENAME,
    PIPELINE_FILENAME,
    pipelines_dir
)


node_manager = NodeManager()
data_manager = DataManager()
decision_unit = DecisionUnit(node_manager, data_manager)
pipeline_manager = PipelineManager(decision_unit, node_manager)
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        func=pipeline_manager.process_pipelines,
        trigger="interval",
        seconds=WAIT_INTERVAL,
    )
    scheduler.add_job(
        func=pipeline_manager.update_pipelines,
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


@app.get("/datasets/update/")
def update_datasets():
    data_manager.update_datasets()
    return {
        "status": "success",
        "message": "Datasets updated successfully",
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
    components_info = []
    for file in components:
        filename = file.filename
        name = filename.split(".")[0].lower().replace("_", "-")
        components_info.append((filename, name))

        content = await file.read()
        with open(path / filename, "wb") as f:
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
    pipeline_manager.add_pipeline(
        pipeline_id=pipeline_id,
        components=components_info
    )

    response = {
        "status": "success",
        "message": "Pipeline submitted successfully",
        "pipeline_id": pipeline_id
    }
    return response
    