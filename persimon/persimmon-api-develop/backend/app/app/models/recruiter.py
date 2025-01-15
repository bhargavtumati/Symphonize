from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Integer, String, ForeignKey
from app.helpers.db_helper import get_metadata

class Recruiter(Base):
    __tablename__ = 'recruiter'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    whatsapp_number: Mapped[str] = mapped_column(String(length=20), nullable=False) 
    designation: Mapped[str] = mapped_column(String(length=255), nullable=False)
    linkedin_url: Mapped[str] = mapped_column(String(length=2048), nullable=False) 
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey('company.id'), nullable=False)
    email_id: Mapped[str] = mapped_column(String(length=255), nullable=False, unique=True)
    meta: Mapped[list[dict]] = mapped_column(JSONB)  

    @classmethod
    def get_by_whatsapp_number(cls, session:Session, whatsapp_number:str):
        return session.query(cls).filter_by(whatsapp_number=whatsapp_number).first()

    @classmethod
    def get_by_email_id(cls, session:Session, email: str):
        return session.query(cls).filter(cls.email_id == email).first()

    @classmethod
    def exists_by_email_id(cls, session: Session, email: str) -> bool:
        return session.query(cls.email_id).filter(cls.email_id == email).scalar() is not None

    def create(self, session: Session, created_by: str):
        self.meta = get_metadata()
        self.meta['audit']['created_by']['email'] = created_by
        session.add(self)
        session.commit()
        session.refresh(self)
        return self
        