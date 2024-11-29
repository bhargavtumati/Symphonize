from fastapi import FastAPI
from .LibraryRouterPack import LibraryRouter
from .LibraryModelPack import LibraryModel
from LibraryManagement import LibraryDatabase

# Create database tables
LibraryModel.Base.metadata.create_all(bind=LibraryDatabase.engine)

app = FastAPI()

app.include_router(LibraryRouter.router, prefix="/api", tags=["library"])

@app.get("/")
def root():
    return {"message":"Welcome to the Library Management System"}