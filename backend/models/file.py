from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from typing import Literal

from config.database import Base


class Request(Base):
    __tablename__ = "requests"

    request_id = Column(String, primary_key=True)
    status = Column(String, default="processing")

    files = relationship("File", back_populates="request")


# Dependant entity
class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    file_path = Column(String)
    request_id = Column(String, ForeignKey("requests.request_id"))

    request = relationship("Request", back_populates="files")
