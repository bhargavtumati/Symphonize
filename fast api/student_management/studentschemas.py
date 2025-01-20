from typing import Optional
from pydantic import BaseModel  # DTO (Data Transfer Object)

class Student(BaseModel):
    name: str
    age: int
    email: str

    class Config:
        from_attributes = True  # Updated to use `from_attributes` instead of `orm_mode`

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
