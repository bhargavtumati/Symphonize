<<<<<<< HEAD
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
=======
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
>>>>>>> 43185ce8265634b14b3d5eef9068476cb3bc7e11
