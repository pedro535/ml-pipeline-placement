import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from typing import List

pipelines_dir = Path("../tmp/pipelines")
pipelines_dir = pipelines_dir.resolve()
pipelines_dir.mkdir(parents=True, exist_ok=True)

app = FastAPI()


@app.get("/")
def handle_root():
    return {"message": "ML pipeline placement system"}


@app.post("/submit/")
async def upload_file(files: List[UploadFile] = File(...)):
    pipeline_id = str(uuid.uuid4())
    path = pipelines_dir / pipeline_id
    path.mkdir(parents=True, exist_ok=True)
    
    file_names = []
    for file in files:
        file_names.append(file.filename)
        content = await file.read()
        with open(path / file.filename, "wb") as f:
            f.write(content)

    return {"message": "Files received", "filenames": file_names, "pipeline_id": pipeline_id}
