from fastapi import HTTPException
from sqlalchemy.orm import Session           #service layer
from . import studentmodel, studentschemas 

# CRUD for students
def create_student(db: Session, student: studentschemas.StudentCreate):
    # Explicitly extract attributes from the Pydantic model (StudentCreate)
    db_student = studentmodel.Student(
        name=student.name,  # Extract 'name' from StudentCreate
        age=student.age,    # Extract 'age' from StudentCreate
        email=student.email # Extract 'email' from StudentCreate
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student



def update_student(db: Session, student_id: int, name: str, age: int, email: str):
    # Fetch the existing student record by ID
    db_student = db.query(studentmodel.Student).filter(studentmodel.Student.id == student_id).first()
    
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    # Update the fields if provided in the request
    if name:
        db_student.name = name
    if age:
        db_student.age = age
    if email:
        db_student.email = email

    # Commit the changes to the database
    db.commit()
    db.refresh(db_student)

    return db_student



def get_students(db: Session, skip: int = 0, limit: int = 10):
    return db.query(studentmodel.Student).offset(skip).limit(limit).all()

def get_student_by_id(db: Session, student_id: int):
    return db.query(studentmodel.Student).filter(studentmodel.Student.id == student_id).first()

def delete_student(db: Session, student_id: int):
    student = db.query(studentmodel.Student).filter(studentmodel.Student.id == student_id).first()
    if student:
        db.delete(student)
        db.commit()
    return student