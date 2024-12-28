from sqlalchemy import BigInteger, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    BookName = Column(String, nullable=False)
    BookAuthor = Column(String, nullable=False)
    BookAvailability = Column(Boolean, default=True)
    UserName = Column(String, nullable=True)
    UserPhoneNumber = Column(BigInteger, nullable=True)
