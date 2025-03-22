from sqlalchemy.orm import Mapped, mapped_column,Session
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import Integer, ForeignKey, String
from app.helpers.db_helper import get_metadata
from app.models.base import Base


class Template(Base):
    __tablename__ = "template"
    __table_args__ = {'schema': 'public'}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey('public.company.id', ondelete='CASCADE'), nullable=False)
    template_data: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), nullable=False)
    email_data: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), nullable=False)
    meta: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), nullable=False)

    @classmethod
    def get_by_company_id(cls, session: Session, id: int):
        return session.query(cls).filter(cls.company_id == id).first()
    
    @classmethod
    def update_template_data(cls, session: Session, id: int, template_data: dict, subject: str, to: list):
        # Fetch the template based on job_id (or company_id)
        template = cls.get_by_job_id(session, id)
        
        if not template:
            return None
        
        # Update the fields you need
        template.template_data = template_data
        template.subject = subject
        template.to = to
        
        # Call the update method to handle commit and refresh
        return template.update(session)

    def create(self, session: Session,created_by:str):
        self.meta = get_metadata()
        self.meta['audit']['created_by']['email'] = created_by
        session.add(self)
        session.commit()
        session.refresh(self)
        return self
    
    def update(self, session: Session):
        session.add(self)
        session.commit()
        session.refresh(self)
        return self