from pydantic import BaseModel   #dto

class Student(BaseModel):
    name: str
    age: int
    email: str

    class Config:
        from_attributes = True  # Updated to use from_attributes instead of orm_mode

class StudentCreate(Student):
    pass

class StudentOut(Student):
    id: int

    class Config:
        from_attributes = True  # Updated setting
