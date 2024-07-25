import uuid

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    BackgroundTasks,
    Depends,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session

from config.database import SessionLocal, engine, Base
from crud import crud
from schema.file import FileRequest, RequestFile

from helper import validate_file, process_file

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/upload")
async def upload(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):

    # Read the file content into memory as bytes
    csv_file_content = await file.read()

    if validate_file(csv_file_content):

        request_id = str(uuid.uuid4())

        db_request: FileRequest = crud.create_request(
            db, request_id=request_id, status="processing"
        )

        if db_request is None:
            return JSONResponse(
                status_code=500,
            )

        # Pass the bytes content to the background task
        background_tasks.add_task(
            process_file, db, csv_file_content, db_request.request_id
        )

        return JSONResponse(content={"requestId": request_id})

    return JSONResponse(
        status_code=404,
        content={"msg": "Invalid CSV file format"},
    )


@app.get("/api/status")
async def status(request_id: str, db: Session = Depends(get_db)):
    db_request: FileRequest = crud.get_request(db, request_id=request_id)
    if db_request is None:
        return JSONResponse(
            content={"error": f"Request with request id {request_id} not found"},
            status_code=400,
        )
    print(db_request.status)
    if db_request.status == "processing":
        return db_request
    elif db_request.status == "completed":
        db_file: RequestFile = crud.get_file(db, request_id=request_id)
        return JSONResponse(
            content={
                "request_id": db_request.request_id,
                "status": db_request.status,
                "file_path": db_file.file_path,
            },
            status_code=200,
        )

    return HTTPException(status_code=500)
