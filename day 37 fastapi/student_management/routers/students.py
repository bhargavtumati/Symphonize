<<<<<<< HEAD
from typing import List            #controller
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database

router = APIRouter()


@router.post("/students/", response_model=schemas.Student)
def create_student(
    name: str,
    age: int,
    email: str,
    db: Session = Depends(database.get_db)
):
    # Create a new student using the provided query parameters
    student_data = schemas.StudentCreate(name=name, age=age, email=email)
    return crud.create_student(db=db, student=student_data)

@router.get("/students/", response_model=List[schemas.Student])
def read_students(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    return crud.get_students(db, skip=skip, limit=limit)

@router.get("/students/{student_id}", response_model=schemas.Student)
def read_student(student_id: int, db: Session = Depends(database.get_db)):
    student = crud.get_student_by_id(db, student_id=student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.delete("/students/{student_id}", response_model=schemas.Student)
def delete_student(student_id: int, db: Session = Depends(database.get_db)):
    student = crud.delete_student(db, student_id=student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
=======
from typing import List            #controller
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database

router = APIRouter()


@router.post("/students/", response_model=schemas.Student)
def create_student(
    name: str,
    age: int,
    email: str,
    db: Session = Depends(database.get_db)
):
    # Create a new student using the provided query parameters
    student_data = schemas.StudentCreate(name=name, age=age, email=email)
    return crud.create_student(db=db, student=student_data)

@router.get("/students/", response_model=List[schemas.Student])
def read_students(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    return crud.get_students(db, skip=skip, limit=limit)

@router.get("/students/{student_id}", response_model=schemas.Student)
def read_student(student_id: int, db: Session = Depends(database.get_db)):
    student = crud.get_student_by_id(db, student_id=student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.delete("/students/{student_id}", response_model=schemas.Student)
def delete_student(student_id: int, db: Session = Depends(database.get_db)):
    student = crud.delete_student(db, student_id=student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
>>>>>>> 43185ce8265634b14b3d5eef9068476cb3bc7e11
