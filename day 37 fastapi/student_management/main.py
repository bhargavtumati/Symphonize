from fastapi import FastAPI       #application class
from .routers import students
from . import models, database

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Include routers
app.include_router(students.router, prefix="/api", tags=["students"])

@app.get("/")
def root():
    return {"message": "Welcome to the Student Management System"}
