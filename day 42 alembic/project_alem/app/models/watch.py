from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
from app.models.base import Base

Base = declarative_base()

class Watch(Base):
    __tablename__ = "watch"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    company = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())


    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"