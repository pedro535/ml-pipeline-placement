import uuid
from typing import List
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from server.components import PipelineManager, DecisionUnit, NodeManager, DataManager
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
    pipeline_manager.dump_pipelines()


app = FastAPI(lifespan=lifespan)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def handle_root():
    return {
        "status": "success",
        "message": "ML pipeline placement system",
    }


@app.get("/pipelines/{pipeline_id}")
def get_pipeline(pipeline_id: str):
    pipeline = pipeline_manager.get_pipeline(pipeline_id)
    if not pipeline:
        return {"status": "error", "message": "Pipeline not found"}
    
    return {
        "status": "success",
        "data": pipeline.dict_repr()
    }


@app.post("/submit/")
async def submit_pipeline(
    name: str = Form(...),
    components: List[UploadFile] = File(...),
    pipeline: UploadFile = File(...),
    metadata: UploadFile = File(...)
):
    # pipeline_id = str(uuid.uuid3())
    pipeline_id = "2864981c-2bdd-47e5-863e-4a185c6e2dcc"
    path = pipelines_dir / pipeline_id
    path.mkdir(parents=True, exist_ok=True)
    
    # Save component files
    components_info = []
    for file in components:
        filename = file.filename
        component_name = filename.split(".")[0].lower().replace("_", "-")
        components_info.append((filename, component_name))

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
    pipeline_manager.add_pipeline(pipeline_id, name, components_info)

    response = {
        "status": "success",
        "message": "Pipeline submitted successfully",
        "pipeline_id": pipeline_id
    }
    return response


print(chr(27) + "[2J")
print(chr(27) + "[H")
print("Pipeline placement system is running...\n")
