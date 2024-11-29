from typing import Optional
from pydantic import BaseModel
from sqlalchemy import BigInteger

class Book(BaseModel):
    BookName:str
    BookAuthor:str
    BookAvailability: Optional[bool] = True
    UserName: Optional[str] = None
    UserPhoneNumber: Optional[int] = None

    class Config:
        from_attributes = True #Updated to use from_attributes instead of orm_mode

class BookCreate(Book):
    pass

class UpdateBook(Book):
    BookName:Optional[str] = None
    BookAuthor:Optional[str] = None
    BookAvailability: Optional[bool] = True
    UserName: Optional[str] = None
    UserPhoneNumber: Optional[int] = None

    class Config:
         from_attributes = True

class BookOut(Book):
    id: int

    class Config:
        from_attributes = True