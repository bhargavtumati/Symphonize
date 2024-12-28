from http.client import HTTPException
from typing import Optional
from sqlalchemy import BigInteger
from sqlalchemy.orm import Session
from LibraryManagement.LibraryModelPack import LibraryModel
from LibraryManagement.LibrarySchemaPack import LibrarySchema

def create_book(db: Session, Library: LibrarySchema.BookCreate):
    new_book = LibraryModel.Book(
        BookName=Library.BookName,
        BookAuthor=Library.BookAuthor,
        BookAvailability=Library.BookAvailability,
        UserName=Library.UserName,
        UserPhoneNumber=Library.UserPhoneNumber
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

def get_book_by_id(db:Session, Book_id: int):
    return db.query(LibraryModel.Book).filter(LibraryModel.Book.id == Book_id).first()

def update_book(db: Session, book_id: int, name: Optional[str], author: Optional[str], availability: Optional[bool], user_name: Optional[str], user_phone: Optional[BigInteger]):
    # Fetch the existing book record by ID
    db_book = db.query(LibraryModel.Book).filter(LibraryModel.Book.id == book_id).first()
    
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    # Update the fields if provided in the request
    if name is not None:
        db_book.BookName = name
    if author is not None:
        db_book.BookAuthor = author
    if availability is not None:
        db_book.BookAvailability = availability
    if user_name is not None:
        db_book.UserName = user_name
    if user_phone is not None:
        db_book.UserPhoneNumber = user_phone

    # Commit the changes to the database

    db.commit()
    db.refresh(db_book)

    return db_book

def delete_book(db: Session, book_id:int):
    db_book =db.query(LibraryModel.Book).filter(LibraryModel.Book.id == book_id).first()
  
    if db_book:
        db.delete(db_book)
        db.commit()
    
    return db_book


