from sqlalchemy import Column, Integer, String, ForeignKey    #entity
from sqlalchemy.orm import relationship
from .database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    email = Column(String(100), unique=True, nullable=False)

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(250))

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

Student.enrollments = relationship("Enrollment", back_populates="student")
Course.enrollments = relationship("Enrollment", back_populates="course")
