from app.models.base import Base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy import func
from app.helpers.db_helper import get_metadata


class ZrJob(Base):
    __tablename__ = "zrjob"
    id: Mapped[int] = mapped_column(primary_key=True)
    detail: Mapped[list[dict]] = mapped_column(JSONB)
    features: Mapped[list[dict]] = mapped_column(JSONB)
    meta: Mapped[list[dict]] = mapped_column(JSONB)

    def __repr__(self) -> str:
        return f"Job(id={self.id!r}, ...)"

    @classmethod
    def get_by_id(cls, session: Session, job_id: str):
        return (
            session.query(cls)
            .filter(func.jsonb_extract_path_text(cls.detail, "job", "id") == job_id)
            .first()
        )

    def create(self, session: Session):
        self.meta = get_metadata()
        session.add(self)
        session.commit()
        session.refresh(self)
        return self.id
