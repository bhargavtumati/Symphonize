from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Integer, String, ForeignKey, LargeBinary, update
from app.helpers.db_helper import get_metadata

class Recruiter(Base):
    __tablename__ = 'recruiter'
    __table_args__ = {'schema': 'public'}
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    whatsapp_number: Mapped[str] = mapped_column(String(length=20), nullable=False) 
    designation: Mapped[str] = mapped_column(String(length=255), nullable=False)
    linkedin_url: Mapped[str] = mapped_column(String(length=2048), nullable=False) 
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey('public.company.id'), nullable=False)
    email_id: Mapped[str] = mapped_column(String(length=255), nullable=False, unique=True)
    profile_image: Mapped[str]= mapped_column(String(length=255), nullable=True)
    gmail_id: Mapped[str] = mapped_column(String(length=255),nullable=True,unique=True)
    meta: Mapped[list[dict]] = mapped_column(JSONB)  

    @classmethod
    def get_by_whatsapp_number(cls, session:Session, whatsapp_number:str):
        return session.query(cls).filter_by(whatsapp_number=whatsapp_number).first()

    @classmethod
    def get_by_email_id(cls, session:Session, email: str):
        return session.query(cls).filter(cls.email_id == email).first()
    
    @classmethod
    def update_profile_image(cls, session: Session, email:str, image_path: str):
        res = session.execute(update(cls).where(cls.email_id == email).values(profile_image=image_path))
        session.commit()
        return res

    @classmethod
    def get_by_created_by_email(cls, session:Session, email: str):
        return session.query(cls).filter(cls.meta['audit']['created_by']['email'].astext == email).first()

    @classmethod
    def exists_by_email_id(cls, session: Session, email: str) -> bool:
        return session.query(cls.email_id).filter(cls.email_id == email).scalar() is not None
    
    @classmethod
    def exists_by_gmail_id(cls, session: Session, gmail_id: str):
        return session.query(cls.email_id).filter(cls.gmail_id == gmail_id).first()

    @classmethod
    def update_details(cls, session: Session, recruiter_id: int, full_name: str=None, whatsapp_number=None, designation=None, linkedin_url=None):
        update_data = {}
        if full_name is not None:
            update_data["full_name"] = full_name
        if whatsapp_number is not None:
            update_data["whatsapp_number"] = whatsapp_number
        if designation is not None:
            update_data["designation"] = designation
        if linkedin_url is not None:
            update_data["linkedin_url"] = linkedin_url
        if update_data: 
            stmt = update(cls).where(cls.id == recruiter_id).values(**update_data)
            session.execute(stmt)
            session.commit()

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
        