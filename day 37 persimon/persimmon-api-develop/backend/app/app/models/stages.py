from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from app.helpers.db_helper import get_metadata


class Stages(Base):
    __tablename__ = "stages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recruiter_id: Mapped[int] = mapped_column(Integer, ForeignKey("recruiter.id"))
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("job.id"))
    stages: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False)

    def __repr__(self) -> str:
        return f"Stages(id={self.id!r}, stages={self.stages!r}, ...)"

    @classmethod
    def get_by_id(cls, session: Session, job_id: int):
        return session.query(cls).filter(cls.job_id == job_id).first()

    def create(self, session: Session, created_by: str):
        self.meta = get_metadata()
        self.meta["audit"]["created_by"]["email"] = created_by
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    def update(self, session: Session):
        session.add(self)
        session.commit()
        session.refresh(self)
        return self
