from app.models.base import Base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.helpers.db_helper import get_metadata

class ZrApplicant(Base):
    __tablename__ = "zrapplicant"
    __table_args__ = {'schema': 'public'}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    candidate_id: Mapped[str]
    applicant_id: Mapped[str]
    job_id: Mapped[str]
    attachments: Mapped[list[dict]] = mapped_column(JSONB)
    meta: Mapped[list[dict]] = mapped_column(JSONB)

    # TODO: Implement stringify
    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, name={self.name!r}, description={self.description}, ...)"

    @classmethod
    def get_by_id(cls, session: Session, applicant_id: str):
        return session.query(cls).filter_by(applicant_id=applicant_id).first()
    
    def create(self, session: Session):
        self.meta = get_metadata()
        session.add(self)
        session.commit()

