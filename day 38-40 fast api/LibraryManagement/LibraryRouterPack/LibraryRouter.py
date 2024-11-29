from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from LibraryManagement.LibrarySchemaPack import LibrarySchema
from LibraryManagement.LibraryServicePack import LibraryService
from  LibraryManagement import LibraryDatabase

router = APIRouter()

@router.post("/library/create", response_model=LibrarySchema.Book)
def create_book(
    BookName: str,
    BookAuthor: str,
    BookAvailability: Optional[bool]=True,
    UserName: Optional[str] = None,  # Optional query parameter
    UserPhoneNumber: Optional[int] = None,  # Optional query parameter
    db: Session = Depends(LibraryDatabase.get_db)
):
    # Pass query params to service
    Library_data = LibrarySchema.BookCreate(
        BookName=BookName,
        BookAuthor=BookAuthor,
        BookAvailability=BookAvailability,
        UserName=UserName,
        UserPhoneNumber=UserPhoneNumber
    )
    return LibraryService.create_book(db=db, Library=Library_data)

@router.get("/library/get", response_model=LibrarySchema.Book)
def read_book(Book_id:int , db:Session = Depends(LibraryDatabase.get_db)):
    library = LibraryService.get_book_by_id(db,Book_id=Book_id)
    if library is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return library

@router.put("/library/update", response_model=LibrarySchema.Book)
def update_book(
    Book_id: int,
    BookName: Optional[str] = None,
    BookAuthor: Optional[str] = None,
    BookAvailability: Optional[bool] = True,
    UserName: Optional[str] = None,
    UserPhoneNumber: Optional[int] = None,
    db: Session = Depends(LibraryDatabase.get_db)
):
    library = LibraryService.get_book_by_id(db,Book_id=Book_id)
    if library is None:
        raise HTTPException(status_code=404, detail="Book not found")
    # Call the update function from LibraryService
    return LibraryService.update_book(
        db=db,
        book_id=Book_id,
        name=BookName,
        author=BookAuthor,
        availability=BookAvailability,
        user_name=UserName,
        user_phone=UserPhoneNumber
    )

@router.delete("/library/delete", response_model=LibrarySchema.Book)
def delete_book(Book_id:int, db:Session=Depends(LibraryDatabase.get_db)):
    library = LibraryService.get_book_by_id(db,Book_id=Book_id)
    if library is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return LibraryService.delete_book(db=db,book_id=Book_id)