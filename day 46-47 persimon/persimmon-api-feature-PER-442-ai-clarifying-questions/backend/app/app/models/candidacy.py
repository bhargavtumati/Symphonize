from app.models.base import Base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy import ForeignKey
from app.helpers.db_helper import get_metadata

class Candidacy(Base):
    __tablename__ = "candidacy"
    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("zrjob.id"))
    resume_id: Mapped[int] = mapped_column(ForeignKey("resume.id"))
    match: Mapped[list[dict]] = mapped_column(JSONB)
    meta: Mapped[list[dict]] = mapped_column(JSONB)

    # TODO: Implement stringify
    def __repr__(self) -> str:
        return f"Candidacy(id={self.id!r}, ...)"

    def create(self, session: Session):
        self.meta = get_metadata()
        session.add(self)
        session.commit()
