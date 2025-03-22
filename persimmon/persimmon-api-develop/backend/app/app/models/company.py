from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Integer, String, Enum, LargeBinary
from sqlalchemy.future import select
import enum
from app.helpers.db_helper import get_metadata
from sqlalchemy.ext.mutable import MutableDict
from typing import List

class CompanyTypeEnum(enum.Enum):
    SERVICE_BASED = 'SERVICE_BASED'
    PRODUCT_BASED = 'PRODUCT_BASED'

class BusinessTypeEnum(enum.Enum):
    B2B = "B2B"  # Business to Business
    B2C = "B2C"  # Business to Consumer
    C2C = "C2C"  # Consumer to Consumer
    C2B = "C2B"  # Consumer to Business
    B2G = "B2G"  # Business to Government
    G2B = "G2B"  # Government to Business
    G2C = "G2C"  # Government to Consumer
    D2C = "D2C"  # Direct to Consumer
    B2B2C = "B2B2C"  # Business to Business to Consumer
    B2B_SaaS = "B2B SaaS"  # Business to Business Software as a Service
    P2P = "P2P"  # Peer to Peer
    M2C = "M2C"  # Manufacturer to Consumer

class Company(Base):
    __tablename__ = 'company'
    __table_args__ = {'schema': 'public'}
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    website: Mapped[str] = mapped_column(String(length=2048), nullable=False)
    number_of_employees: Mapped[str] = mapped_column(String(length=50), nullable=False) 
    industry_type: Mapped[str] = mapped_column(String(length=255), nullable=False)
    linkedin: Mapped[str] = mapped_column(String(length=2048), nullable=False)
    domain: Mapped[str] = mapped_column(String(length=255), nullable=False, unique=True)
    type: Mapped[CompanyTypeEnum] = mapped_column(Enum(CompanyTypeEnum, name='CompanyType', schema='enum'), nullable=False)
    tagline: Mapped[str] = mapped_column(String(length=255), nullable=True)
    business_type: Mapped[BusinessTypeEnum] = mapped_column(Enum(BusinessTypeEnum, name='BusinessType', schema='enum'), nullable=True) 
    about: Mapped[str] = mapped_column(String(length=1000), nullable=True)
    logo: Mapped[str] = mapped_column(String, nullable=True)
    images: Mapped[list[str]] = mapped_column(JSONB, nullable=True)
    instagram: Mapped[str] = mapped_column(String(length=2048), nullable=True)
    facebook: Mapped[str] = mapped_column(String(length=2048), nullable=True)
    twitter: Mapped[str] = mapped_column(String(length=2048), nullable=True)
    meta: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB))

    @classmethod
    def get_by_id(cls, session: Session, company_id: int):
        return session.query(cls).filter_by(id=company_id).first()

    @classmethod
    def get_by_name(cls, session: Session, company_name: str):
        if company_name:
            return session.query(cls).filter(cls.name.ilike(f"%{company_name}%")).all()

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

    @classmethod
    def remove_image(cls, session: Session, company_id: int, new_images: List[str]):
        session.query(cls).filter(cls.id == company_id).update({cls.images: new_images})
        session.commit()

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith("_")}