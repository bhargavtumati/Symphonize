from sqlalchemy import Integer, String, ForeignKey, and_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.helpers.db_helper import get_metadata
from app.models.base import Base

class Integration(Base):
    __tablename__ = "integration"
    __table_args__ = {'schema': 'public'}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    credentials: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), nullable=False)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey('public.company.id'))
    meta: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), nullable=False)

    def __repr__(self) -> str:
        return f"<Integration(id={self.id}, type={self.type}, credentials={self.credentials}, meta={self.meta}, company_id={self.company_id})>"

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
    def get_credentials(cls, session: Session, company_id: int, platform_name: str):
        return session.query(cls).filter(and_(cls.company_id == company_id, cls.type == platform_name)).first()