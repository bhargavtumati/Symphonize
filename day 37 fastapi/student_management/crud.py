from sqlalchemy.orm import Session           #service layer
from . import models, schemas 

# CRUD for students
def create_student(db: Session, student: schemas.StudentCreate):
    # Explicitly extract attributes from the Pydantic model (StudentCreate)
    db_student = models.Student(
        name=student.name,  # Extract 'name' from StudentCreate
        age=student.age,    # Extract 'age' from StudentCreate
        email=student.email # Extract 'email' from StudentCreate
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student
def get_students(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Student).offset(skip).limit(limit).all()

def get_student_by_id(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def delete_student(db: Session, student_id: int):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student:
        db.delete(student)
        db.commit()
    return student
