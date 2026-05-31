from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.db.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    saved_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    extracted_text = Column(Text, nullable=False)
    document_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)