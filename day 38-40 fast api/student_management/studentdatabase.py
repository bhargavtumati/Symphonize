<<<<<<< HEAD:day 37 fastapi/student_management/database.py
<<<<<<< HEAD
from sqlalchemy import create_engine          #repo layer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/student_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
=======
from sqlalchemy import create_engine          #repo layer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/student_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
>>>>>>> 43185ce8265634b14b3d5eef9068476cb3bc7e11
=======
from sqlalchemy import create_engine          #repo layer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#//username:password@address
DATABASE_URL = "postgresql://postgres:root@localhost:5432/student_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
>>>>>>> d7d2c03942e41a7dbf00d34af51360e0d2224a92:day 38-40 fast api/student_management/studentdatabase.py
