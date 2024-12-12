from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Integer, String, Enum
from sqlalchemy.future import select
import enum
from app.helpers.db_helper import get_metadata
from sqlalchemy.ext.mutable import MutableDict

class CompanyTypeEnum(enum.Enum):
    SERVICE_BASED = 'SERVICE_BASED'
    PRODUCT_BASED = 'PRODUCT_BASED'

class Company(Base):
    __tablename__ = 'company'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    website: Mapped[str] = mapped_column(String(length=2048), nullable=False)
    number_of_employees: Mapped[str] = mapped_column(String(length=50), nullable=False) 
    industry_type: Mapped[str] = mapped_column(String(length=255), nullable=False)
    linkedin: Mapped[str] = mapped_column(String(length=2048), nullable=False)
    domain: Mapped[str] = mapped_column(String(length=255), nullable=False, unique=True)
    type: Mapped[CompanyTypeEnum] = mapped_column(Enum(CompanyTypeEnum, name='CompanyType', schema='enum'), nullable=False)
    meta: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB))

    @classmethod
    def get_by_id(cls, session: Session, company_id: int):
        return session.query(cls).filter_by(id=company_id).first()

    @classmethod
    def get_by_name(cls, session: Session, company_name: str):
        if company_name:
            return session.query(cls).filter(cls.name.ilike(f"%{company_name}%")).first()

    @classmethod
    def get_by_domain(cls, session: Session, domain: str):
        result = session.execute(select(cls).where(cls.domain == domain))
        company = result.scalars().first()
        return company

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

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith("_")}