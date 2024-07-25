from sqlalchemy.orm import Session

from models.file import File, Request


def create_file(db: Session, request_id: str, file_path: str):
    db_file = File(request_id=request_id, file_path=file_path)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def get_file(db: Session, request_id: str):
    return db.query(File).filter(File.request_id == request_id).first()


def get_request(db: Session, request_id: str):
    return db.query(Request).filter(Request.request_id == request_id).first()


def update_request(db: Session, request_id: str, status: str):
    db_request = db.query(Request).filter(Request.request_id == request_id).first()

    # update request if exist
    if db_request:
        db_request.status = status
        db.commit()
        db.refresh(db_request)
        return db_request

    # create request if not exist
    return create_request(db, request_id=request_id, status=status)


def create_request(db: Session, request_id: str, status: str):
    db_request = Request(request_id=request_id, status=status)
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request
