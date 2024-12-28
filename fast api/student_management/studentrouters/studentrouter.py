from typing import List            #controller
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import studentservice, studentschemas, studentdatabase

router = APIRouter()


@router.post("/students/", response_model=studentschemas.Student)
def create_student(
    name: str,
    age: int,
    email: str,
    db: Session = Depends(studentdatabase.get_db)
):
    # Create a new student using the provided query parameters
    student_data = studentschemas.StudentCreate(name=name, age=age, email=email)
    return studentservice.create_student(db=db, student=student_data)

@router.get("/students/", response_model=List[studentschemas.Student])
def read_all_students(skip: int = 0, limit: int = 10, db: Session = Depends(studentdatabase.get_db)):
    return studentservice.get_students(db, skip=skip, limit=limit)

@router.get("/students/{student_id}", response_model=studentschemas.Student)
def read_student(student_id: int, db: Session = Depends(studentdatabase.get_db)):
    student = studentservice.get_student_by_id(db, student_id=student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# Define the endpoint to update a student
@router.put("/students/{student_id}", response_model=studentschemas.Student)
def update_student_endpoint(
    student_id: int,
    name: str,
    age: int,
    email: str,
   db: Session = Depends(studentdatabase.get_db) # Dependency to get the DB session
):
    # Call the update_student function
    return studentservice.update_student(db, student_id=student_id, name=name,age=age,email=email)

@router.delete("/students/{student_id}", response_model=studentschemas.Student)
def delete_student(student_id: int, db: Session = Depends(studentdatabase.get_db)):
    student = studentservice.delete_student(db, student_id=student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
