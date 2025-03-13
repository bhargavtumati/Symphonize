from app.helpers.db_helper import get_metadata
from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, Session

from app.models.base import Base

class Shared(Base):
    __tablename__ = 'shared'
    __table_args__ = {'schema': 'public'}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    details: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False)

    @classmethod
    def get_by_uuid(cls, session: Session, uuid: str):
        return session.query(cls).filter(cls.uuid == uuid).first()

    def create(self, session: Session, created_by:str):
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