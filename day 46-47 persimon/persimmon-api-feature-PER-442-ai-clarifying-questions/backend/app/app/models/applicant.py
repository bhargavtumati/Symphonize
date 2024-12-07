from app.models.base import Base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String, func,desc,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.helpers.db_helper import get_metadata
from sqlalchemy.ext.mutable import MutableDict


class Applicant(Base):
    __tablename__ = "applicant"
    id: Mapped[int] = mapped_column(primary_key=True)
    details : Mapped[list[dict]] = mapped_column(JSONB,nullable=False) 
    uuid: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    stage_uuid : Mapped[str] = mapped_column(String,nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"))
    meta: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB),nullable=False)

    # TODO: Implement stringify
    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, name={self.name!r}, description={self.description}, ...)"
        
    @classmethod
    def get_by_stage_uuid(cls, session: Session, stage_uuid: str):
        return session.query(cls).filter(cls.stage_uuid == stage_uuid).all()
    
    @classmethod
    def get_by_id(cls, session: Session, id: int):
        return session.query(cls).filter(cls.id == id).first()

    @classmethod
    def get_by_uuid(cls, session: Session, uuid: str):
        return session.query(cls).filter(cls.uuid == uuid).first()

    @classmethod
    def get_count(cls, session: Session, job_id : int, stage_uuid:str, name:str = None) -> int:
        query = session.query(cls).filter(cls.job_id == job_id)
        if stage_uuid:
            query = query.filter(cls.stage_uuid == stage_uuid)
        if name:
            query = query.filter(cls.details["personal_information"].cast(JSONB)["full_name"].astext.ilike(f"%{name}%"))
        return query.count()
        
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

