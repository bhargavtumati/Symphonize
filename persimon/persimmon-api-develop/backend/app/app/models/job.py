from app.models.base import Base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, Session,aliased
from sqlalchemy import Enum, Boolean, ForeignKey, String, Integer, desc, Float, DateTime, func, asc, and_, Case, label, or_
import enum
from app.helpers.db_helper import get_metadata
from app.models.company import Company
from sqlalchemy.ext.mutable import MutableDict
from app.helpers.jd_helper import extract_features_from_jd
from app.models.applicant import Applicant
from sqlalchemy import cast, Date
import app.helpers.date_helper as date_helper

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
    __table_args__ = {'schema': 'public'}
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

    company_id: Mapped[int] = mapped_column(Integer, ForeignKey('public.company.id'))
    ai_clarifying_questions: Mapped[list[dict]] = mapped_column(JSONB, default=[])

    # New fields for publishing options
    publish_on_career_page: Mapped[bool] = mapped_column(Boolean, default=True)
    publish_on_job_boards: Mapped[list[str]] = mapped_column(JSONB, default=[])

    #meta data
    meta: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB),nullable=False)
    def __repr__(self) -> str:
        return f"Job(id={self.id!r}, ...)"

    @classmethod
    def filter_query(cls, query, created_by_email: str, client_name: str, code: str = None, title: str = None, location: str = None, company:Company = None,target_date: str = None, posted_on : str = None):
        if client_name and len(client_name) and (not company):
            return {
                'query': query,
                'allow_retrieve': False
            }
        query = query.filter(func.jsonb_extract_path_text(cls.meta, 'audit', 'created_by', 'email') == created_by_email)
        if code:
            query = query.filter(cls.code.ilike(f"%{code}%"))
        if title:
            query = query.filter(cls.title.ilike(f"%{title}%"))
        if location:
            query = query.filter(cls.location.ilike(f"%{location}%"))
        if company:
            query = query.filter(cls.company_id == company.id)
        if posted_on:
            query = date_helper.date_filter_query_helper(query = query, search_date = posted_on, 
                        date_field = func.to_timestamp(cls.meta['audit']['created_at'].astext.cast(Float)))
        if target_date:
            query = date_helper.date_filter_query_helper(query = query, search_date = target_date, date_field = Job.target_date)
                
        return {
                'query': query,
                'allow_retrieve': True
            }


    
    @classmethod
    def get_count(cls, session: Session, code: str, title: str, location: str, company: Company, client_name:str, created_by_email: str,target_date: str, posted_on : str) -> int:
        query = session.query(cls)
        query = cls.filter_query(query=query, client_name=client_name, code=code, title=title, location=location, company=company, created_by_email=created_by_email,target_date=target_date, posted_on=posted_on)
        if not query['allow_retrieve']:
            return 0
        return query['query'].count()

    @classmethod
    def get_all(cls, session: Session, limit: int, offset: int, code: str, title: str, location: str, company: Company, client_name: str, target_date: str, posted_on: str, created_by_email: str,sort_order:str,sort_column:str):
        CompanyAlias = aliased(Company)
        applicant_count_subquery = (
            session.query(
                Applicant.job_id,
                func.count(Applicant.id).label("applicant_count")
            )
            .filter(func.jsonb_extract_path_text(Applicant.status, 'overall_status') == 'success')
            .group_by(Applicant.job_id)
            .subquery()
        )

        query = (
            session.query(
                cls,
                label("applicant_count", func.coalesce(applicant_count_subquery.c.applicant_count, 0)),
                CompanyAlias.name.label("client_name")
            )
            .outerjoin(applicant_count_subquery, cls.id == applicant_count_subquery.c.job_id)
            .outerjoin(CompanyAlias, cls.company_id == CompanyAlias.id) 
        )

        if sort_order=="asc":
            if sort_column=="posted_on":
                query = query.order_by(asc(cls.meta['audit']['created_at']))
            elif sort_column=="applicant_count":
                query = query.order_by(asc("applicant_count"))
            elif sort_column=="status":
                query = query.order_by(
                    Case(
                        (Job.status == JobStatusTypeEnum.ACTIVE.value, 0), else_=1
                    ).asc(),
                    Job.code.asc()
                )
            elif sort_column=="client_name":
                query = query.order_by(asc("client_name"))
            else:
                query = query.order_by(asc(getattr(cls, sort_column)))
        else:
            if sort_column=="posted_on":
                query = query.order_by(desc(cls.meta['audit']['created_at']))
            elif sort_column=="applicant_count":
                query = query.order_by(desc("applicant_count"))
            elif sort_column=="status":
                query = query.order_by(
                    Case(
                        (Job.status == JobStatusTypeEnum.ACTIVE.value, 0), else_=1
                    ).desc(), 
                    Job.code.asc()
                )
            elif sort_column=="client_name":
                query = query.order_by(desc("client_name"))
            else:
                query = query.order_by(desc(getattr(cls, sort_column)))

        query = cls.filter_query(query=query, client_name=client_name, code=code, title=title, location=location, company=company,target_date=target_date, posted_on=posted_on, created_by_email=created_by_email)        
        if not query['allow_retrieve']:
            return [] 
        results = query['query'].offset(offset).limit(limit).all()
        jobs_with_additional_fields = [
            {
                **job.__dict__,
                "applicant_count": applicant_count,
                "client_name": client_name
            }
            for job, applicant_count, client_name in results
        ]

        return jobs_with_additional_fields

    @classmethod
    def get_by_id(cls, session: Session, id: int, email: str):
        return session.query(cls).filter(and_(cls.id == id, func.jsonb_extract_path_text(cls.meta, 'audit', 'created_by', 'email') == email)).first()
    
    @classmethod
    def get_id_by_code(cls,session:Session,code:str):
        job = session.query(cls.id).filter(cls.code == code).first()
        return job.id 

    @classmethod
    def get_by_code(cls, session: Session, code: str):
        job = session.query(cls).filter(cls.code == code).first()
        return job
    
    
    @classmethod
    def search_jobs_by_domain(cls, session: Session, domain: str, search_term: str = None):
        query = session.query(cls).filter(
            and_(
                func.split_part(cls.meta["audit"]["created_by"]["email"].astext, '@', 2) == domain,
                cls.publish_on_career_page == True,
                cls.status == JobStatusTypeEnum.ACTIVE,
            )
        )

        if search_term:
            query = query.filter(
                or_(
                    cls.location.ilike(f"%{search_term}%"),  
                    cls.title.ilike(f"%{search_term}%"), 
                )
            )

        query = query.order_by(desc(cls.meta['audit']['created_at']))
        return query.all()
    
    @classmethod
    def load_enhanced_jd(cls, session: Session):
        jobs = session.query(cls).all()
        for job in jobs:
            if job.enhanced_description=={}:
                enhanced_jd = extract_features_from_jd(job.description)
                enhanced_jd.setdefault("salary", {})
                enhanced_jd.setdefault("company_size", {})
                enhanced_jd.setdefault("team_size", {})
                enhanced_jd.setdefault("location", {})
                enhanced_jd.setdefault("workmode", {})
                enhanced_jd["salary"]["max_value"] = job.max_salary
                enhanced_jd["salary"]["min_value"] = job.min_salary
                company_details: Company = Company.get_by_id(session=session, company_id=job.company_id)
                enhanced_jd["company_size"]["value"] = company_details.number_of_employees
                enhanced_jd["company_size"]["preference"] =  "Good to have"
                enhanced_jd["team_size"]["value"] = job.team_size
                enhanced_jd["team_size"]["preference"] =  "Good to have"
                enhanced_jd["location"]["first_priority"] = job.location
                enhanced_jd["location"]["second_priority"] = "Any"
                enhanced_jd["workmode"]["value"] = "Any"
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

    @classmethod
    def get_all_applicants_count(cls,session:Session,job_id:int):
        result = (
        session.query(func.count(Applicant.id))
        .filter(and_(Applicant.job_id == job_id, func.jsonb_extract_path_text(Applicant.status, 'overall_status') == 'success'))
        .scalar()
        )
        return result
    
    @classmethod
    def get_code_with_id(cls,session:Session,id:int):
        result = (
        session.query(cls.code)
        .filter(cls.id == id)
        .scalar()
        )
        return result
    
    
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
    