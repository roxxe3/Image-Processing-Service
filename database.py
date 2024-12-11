
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, ForeignKey, DateTime
import uuid
from sqlalchemy.sql import func



engine = create_engine("sqlite:///mydatabase.db", echo=True)
Base = declarative_base()

class User(Base):
    __tablename__="users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String)
    password = Column(String)

class Image(Base):
    __tablename__ = "images"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)  # Assuming a 'users' table
    filename = Column(String, nullable=False)
    url = Column(Text, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=True)  # File size in bytes
    mime_type = Column(String, nullable=False)  # e.g., "image/png"
    transformations = Column(Text, nullable=True)  # Store JSON as a string


Base.metadata.create_all(engine)