from pydantic import BaseModel


class FileRequest(BaseModel):
    request_id: str
    status: str


class RequestFile(BaseModel):
    file_path: str
    request_id: str
