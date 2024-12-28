from sqlalchemy import Integer, func, and_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.helpers.db_helper import get_metadata
from app.models.base import Base


class Customization(Base):
    __tablename__ = "customizations"

    # Column definitions using Mapped for type hinting
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meta: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB))  # Metadata column
    settings: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB))  # All other fields in JSONB

    # Represent the object as a string for easier debugging
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

    @classmethod
    def get_by_domain(cls, session: Session, domain: str, email: str):
        """
        Retrieves a Customization record by its domain and creator's email.

        Args:
            session (Session): SQLAlchemy session for querying the database.
            domain (str): The domain name to search for.
            email (str): The email of the creator (nested in JSONB).

        Returns:
            Customization or None: The matching record or None if not found.
        """
        # Query to retrieve a Customization based on domain and email
        return session.query(cls).filter(
            and_(
                func.jsonb_extract_path_text(cls.settings, 'domain') == domain,
                func.jsonb_extract_path_text(cls.meta, 'audit', 'created_by', 'email') == email
            )
        ).first()
