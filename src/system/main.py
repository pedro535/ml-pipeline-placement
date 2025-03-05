from fastapi import FastAPI, UploadFile
from typing import List

app = FastAPI()


@app.get("/")
def handle_root():
    return {"message": "ML pipeline placement system"}


@app.post("/uploadfile/")
async def upload_file(files: List[UploadFile]):
    for file in files:
        print("File name:", file.filename)
        print("Content type:", file.content_type)
        
        content = await file.read()
        with open(f"submissions/{file.filename}", "wb") as f:
            f.write(content)

    return {"message": "File uploaded successfully"}
