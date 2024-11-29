from fastapi import FastAPI       #application class
from .studentrouters import studentrouter
from . import studentmodel, studentdatabase

# Create database tables
studentmodel.Base.metadata.create_all(bind=studentdatabase.engine)

app = FastAPI()

# Include routers
app.include_router(studentrouter.router, prefix="/api", tags=["students"])

@app.get("/")
def root():
    return {"message": "Welcome to the Student Management System"}
