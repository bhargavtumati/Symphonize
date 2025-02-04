from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.helpers.db_helper import get_metadata
from app.models.base import Base


class Resume(Base):
    __tablename__ = "resume"
    __table_args__ = {'schema': 'public'}
    id: Mapped[int] = mapped_column(primary_key=True)
    detail: Mapped[list[dict]] = mapped_column(JSONB)
    features: Mapped[list[dict]] = mapped_column(JSONB)
    meta: Mapped[list[dict]] = mapped_column(JSONB)

    def __repr__(self) -> str:
        return f"Resume(id={self.id!r}, ...)"

    @classmethod
    def get_by_id(cls, session: Session, attachment_id: str):
        return session.query(cls).filter(func.jsonb_extract_path_text(cls.detail, 'attachment', 'id') == attachment_id).first()

    def create(self, session: Session):
        self.meta = get_metadata()
        session.add(self)
        session.commit()
        session.refresh(self)
        return self.id