from sqlalchemy import Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.helpers.db_helper import get_metadata
from app.models.base import Base

class Customization(Base):
    __tablename__ = "customization"
    __table_args__ = {'schema': 'public'}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey('public.company.id'), nullable=False)
    settings: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), nullable=False)
    meta: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), nullable=False)

    def __repr__(self) -> str:
        return f"<Customization(id={self.id}, settings={self.settings}, meta={self.meta}, company_id={self.company_id})>"

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
    def get_customization_settings(cls, session: Session, company_id: int):
        return session.query(cls).filter(cls.company_id == company_id).first()