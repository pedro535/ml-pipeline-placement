import uuid
import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from typing import List
import subprocess

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

    response = {
        "status": "success",
        "pipeline_id": pipeline_id,
        "files": file_names
    }
    return response


@app.get("/tests/")
def tests():
    result = subprocess.run(
        ["python3", pipelines_dir / "1" / "teste.py", "-p", "node1", "node2"],
        capture_output=True,
        cwd=pipelines_dir / "1"
    )
    return {"output": result.stdout.decode("utf-8")}
