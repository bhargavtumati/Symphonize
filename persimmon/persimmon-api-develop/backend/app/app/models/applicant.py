from app.models.base import Base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String, func, desc, ForeignKey, and_, or_
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.helpers.db_helper import get_metadata
from sqlalchemy.ext.mutable import MutableDict
from typing import List
import enum

import logging

logger = logging.getLogger(__name__)

class InterviewType(enum.Enum):
    ONLINE = 'ONLINE'
    FACE_TO_FACE = 'FACE_TO_FACE'
    PHONE_CALL = 'PHONE_CALL'

class Applicant(Base):
    __tablename__ = "applicant"
    __table_args__ = {'schema': 'public'}
    id: Mapped[int] = mapped_column(primary_key=True)
    details : Mapped[list[dict]] = mapped_column(JSONB,nullable=False) 
    status : Mapped[list[dict]] = mapped_column(JSONB,nullable=True) 
    uuid: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    stage_uuid : Mapped[str] = mapped_column(String,nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("public.job.id"))
    meta: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB),nullable=False)

    # TODO: Implement stringify
    def __repr__(self) -> str:
        return f"Applicant(id={self.id!r}, ...)"
        
    @classmethod
    def get_by_stage_uuid(cls, session: Session, stage_uuid: str):
        return session.query(cls).filter(cls.stage_uuid == stage_uuid).all()
    
    @classmethod
    def get_by_id(cls, session: Session, id: int):
        return session.query(cls).filter(cls.id == id).first()
    
    @classmethod
    def get_by_emailid(cls,session:Session,emailid:str):
        return session.query(cls).filter(func.jsonb_extract_path_text(cls.details, 'personal_information', 'email') == emailid).first()
    
    @classmethod
    def get_by_emailid_and_job_id(cls,session:Session, emailid:str, job_id: int):
        return session.query(cls).filter(func.jsonb_extract_path_text(cls.details, 'personal_information', 'email') == emailid, cls.job_id == job_id).first()

    @classmethod
    def get_by_uuid(cls, session: Session, uuid: str):
        return session.query(cls).filter(cls.uuid == uuid).first()
    
    @classmethod
    def get_by_gcp_path(cls, session: Session, gcp_path: str):
        return session.query(Applicant).filter(Applicant.details["file_upload"].astext == gcp_path).scalar()
   
    @classmethod
    def get_id_by_original_path(cls, session: Session, gcp_path: str):
        return session.query(Applicant).filter(Applicant.details["original_resume"].astext == gcp_path).scalar()

    @classmethod
    def get_all_by_original_path(cls, session: Session, file_paths: List[str]):
        return session.query(cls).filter(Applicant.details["original_resume"].astext.in_(file_paths)).all()

    @classmethod
    def get_count(cls, session: Session, job_id : int, stage_uuid:str) -> int:
        return session.query(cls).filter(and_(cls.job_id == job_id, cls.stage_uuid == stage_uuid, or_(cls.status.is_(None),func.jsonb_extract_path_text(cls.status, 'overall_status') == 'success'))).count()
        
    @classmethod
    def get_all(cls, session: Session, limit: int, offset: int, job_id: int, stage_uuid:str, name:str = None):
        query = session.query(cls).filter(cls.job_id == job_id)
        if stage_uuid:
            query = query.filter(cls.stage_uuid == stage_uuid)
        if name:
            query = query.filter(
                cls.details["personal_information"].cast(JSONB)["full_name"].astext.ilike(f"%{name}%")
            )
        return (
            query
            .order_by(desc(cls.meta['audit']['created_at']))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create(self, session: Session,created_by:str):
        try:
            self.meta = get_metadata()
            self.meta['audit']['created_by']['email'] = created_by
            session.add(self)
            session.commit()
            session.refresh(self)
        except Exception as e:
            session.rollback()
            logger.error(f"Transaction failed, rolled back: {e}", exc_info=True) 
            raise
        return self
    
      
    def update(self, session: Session):
        try:
            session.add(self)
            session.commit()
            session.refresh(self)
        except Exception as e:
            session.rollback()
            logger.error(f"Transaction failed, rolled back: {e}", exc_info=True) 
            raise 
        return self

