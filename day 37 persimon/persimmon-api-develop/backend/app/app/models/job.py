from app.models.base import Base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy import Enum, Boolean, ForeignKey, String, Integer, desc, Float, DateTime, func
import enum
from app.helpers.db_helper import get_metadata
from app.models.company import Company
from sqlalchemy.ext.mutable import MutableDict
from app.helpers.jd_helper import extract_features_from_jd

# Enum definitions
class JobTypeEnum(enum.Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    FREELANCE = "FREELANCE"
    CONTRACT = "CONTRACT"
    INTERNSHIP = "INTERNSHIP"

class WorkplaceTypeEnum(enum.Enum):
    ON_SITE = "ON_SITE"
    HYBRID = "HYBRID"
    REMOTE = "REMOTE"

class JobStatusTypeEnum(enum.Enum):
    ACTIVE = 'ACTIVE'
    CLOSED = 'CLOSED'

# Model definition
class Job(Base):
    __tablename__ = "job"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Mandatory fields with non-nullable constraint
    code: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[JobTypeEnum] = mapped_column(Enum(JobTypeEnum, name='JobType', schema='enum'), nullable=False)
    status: Mapped[JobStatusTypeEnum] = mapped_column(Enum(JobStatusTypeEnum, name='JobStatusType', schema='enum'), default='ACTIVE')
    workplace_type: Mapped[WorkplaceTypeEnum] = mapped_column(Enum(WorkplaceTypeEnum, name='WorkplaceType', schema='enum'), nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    team_size: Mapped[str] = mapped_column(String, nullable=False)
    min_salary: Mapped[float] = mapped_column(Float, nullable=False)
    max_salary: Mapped[float] = mapped_column(Float, nullable=False)
    min_experience: Mapped[int] = mapped_column(Integer, nullable=False)
    max_experience: Mapped[int] = mapped_column(Integer, nullable=False)
    target_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    enhanced_description: Mapped[list[str]] = mapped_column(JSONB, nullable=False)

    #Toggle field for client posting
    is_posted_for_client: Mapped[bool] = mapped_column(Boolean, default=False)

    company_id: Mapped[int] = mapped_column(Integer, ForeignKey('company.id'))
    ai_clarifying_questions: Mapped[list[dict]] = mapped_column(JSONB, default=[])

    # New fields for publishing options
    publish_on_career_page: Mapped[bool] = mapped_column(Boolean, default=True)
    publish_on_job_boards: Mapped[list[str]] = mapped_column(JSONB, default=[])

    #meta data
    meta: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB),nullable=False)
    def __repr__(self) -> str:
        return f"Job(id={self.id!r}, ...)"

    @classmethod
    def filter_query(cls, query, created_by_email: str, client_name: str, id: int = None, title: str = None, location: str = None, company:Company = None):
        if client_name and len(client_name) and (not company):
            return {
                'query': query,
                'allow_retrieve': False
            }

        query = query.filter(func.jsonb_extract_path_text(cls.meta, 'audit', 'created_by', 'email') == created_by_email)
        if id:
            query = query.filter(cls.id == id)
        if title:
            query = query.filter(cls.title.ilike(f"%{title}%"))
        if location:
            query = query.filter(cls.location.ilike(f"%{location}%"))
        if company:
            query = query.filter(cls.company_id == company.id)
        return {
                'query': query,
                'allow_retrieve': True
            }

    @classmethod
    def get_count(cls, session: Session, id: int, title: str, location: str, company: Company, client_name:str, created_by_email: str) -> int:
        query = session.query(cls)
        query = cls.filter_query(query=query, client_name=client_name, id=id, title=title, location=location, company=company, created_by_email=created_by_email)
        if not query['allow_retrieve']:
            return 0
        return query['query'].count()

    @classmethod
    def get_all(cls, session: Session, limit: int, offset: int, id: int, title: str, location: str, company: Company, client_name: str, created_by_email: str):
        query = session.query(cls).order_by(desc(cls.meta['audit']['created_at']))
        query = cls.filter_query(query=query, client_name=client_name, id=id, title=title, location=location, company=company, created_by_email=created_by_email)
        if not query['allow_retrieve']:
            return []
        return query['query'].offset(offset).limit(limit).all()

    @classmethod
    def get_by_id(cls, session: Session, id: int):
        return session.query(cls).filter(cls.id == id).first()
    
    
    @classmethod
    def load_enhanced_jd(cls, session: Session):
        jobs = session.query(cls).all()
        for job in jobs:
            if job.enhanced_description=={}:
                enhanced_jd = extract_features_from_jd(job.description)
                job.enhanced_description = enhanced_jd
        session.commit()

    @classmethod
    def get_next_sequence_number(cls, session: Session, company_code: str): 
        max_sequence = session.query(
            func.max(
                func.cast(
                    func.substring(cls.code, 4, func.length(cls.code) - 3), Integer
                )
            )
        ).filter(cls.code.like(f"{company_code}%")).scalar()  
        next_sequence = (max_sequence or 0) + 1 
        return next_sequence

    def create(self, session: Session, created_by: str):
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
    