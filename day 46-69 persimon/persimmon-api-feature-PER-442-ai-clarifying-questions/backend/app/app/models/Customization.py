from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from app.helpers.db_helper import get_metadata



class Customization(Base):
    __tablename__ = "customizations"

    # Column definitions using Mapped for type hinting
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meta: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB))  # Metadata column
    settings: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB))  # All other fields in JSONB

    def __repr__(self) -> str:
        return f"<Customization(id={self.id}, settings={self.settings}, meta={self.meta})>"

    # Method to create a new customization using metadata
    def create(self, session: Session, created_by: str):
        self.meta = get_metadata()
        self.meta['audit']['created_by']['email'] = created_by
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    # Method to update an existing customization using metadata
    def update(self, session: Session):
        session.add(self)
        session.commit()
        session.refresh(self)
        return self
