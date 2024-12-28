<<<<<<< HEAD:day 37 fastapi/student_management/schemas.py
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
=======
from typing import Optional
from pydantic import BaseModel   #dto

class Student(BaseModel):
    name: str
    age: int
    email: str

    class Config:
        from_attributes = True  # Updated to use from_attributes instead of orm_mode

class StudentCreate(Student):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True

class StudentOut(Student):
    id: int

    class Config:
        from_attributes = True  # Updated setting
>>>>>>> d7d2c03942e41a7dbf00d34af51360e0d2224a92:day 38-40 fast api/student_management/studentschemas.py
