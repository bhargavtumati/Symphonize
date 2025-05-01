import os
import json

from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy import Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import Base
from app.db.session import SessionLocal

class MasterData(Base):
    __tablename__ = 'master_data'
    __table_args__ = {'schema': 'public'}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f"MasterData(id={self.id!r}, type={self.type!r})"

    @classmethod
    def validate_value_by_type(cls, key: str, value: str, type: str):
        with SessionLocal() as session:
            value_exists = session.query(cls).filter(
                cls.type == type,
                func.jsonb_exists(cls.value, key),
                func.lower(cls.value[key].astext) == value.strip().lower()
            ).first()
            session.close()
            return value_exists    

    @classmethod
    def get_all_by_type(cls, session: Session, type: str):
        return session.query(cls.value['name'].astext).filter_by(type=type).all()
    
    @classmethod
    def get_all_designations(cls, session: Session):
        return session.query(cls.value['title'].astext).filter_by(type='designation').all()
    
    def get_existing_record(self, session: Session, key: str = "name"):
        # Extract name from JSONB value
        name_value = self.value.get(key, "").strip().lower()

        # Check if the record already exists
        existing_record = session.query(MasterData).filter(
            MasterData.type == self.type,
            func.jsonb_exists(MasterData.value, key),
            func.lower(MasterData.value[key].astext) == name_value
        ).first()
        return existing_record
        
    def create(self, session: Session):
        session.add(self)
        session.commit()
        session.refresh(self)

    @classmethod
    def seed_master_data(cls, session: Session):
        current_dir = os.path.dirname(__file__)
        industry_types_json_file = os.path.join(current_dir, '..', 'datasets', 'industry_types.json')
        indian_cities_json_file = os.path.join(current_dir, '..', 'datasets', 'indian_cities.json')
        
        with open(industry_types_json_file, mode='r') as file:
            industry_types = json.load(file)

        with open(indian_cities_json_file, mode='r') as file:
            indian_cities = json.load(file)

        industry_type_exists = session.query(cls).filter_by(type='Industry Type').all()
        names = {entry.value['name'] for entry in industry_type_exists if 'name' in entry.value}
        location_exists = session.query(cls).filter_by(type='location').all()
        states = {entry.value['state'] for entry in location_exists if 'state' in entry.value}

        new_entries = []
        for industry_type in industry_types:
            if industry_type['name'] not in names:
                industry_type = cls(value=industry_type, type="Industry Type")
                industry_type.create(session=session)
                new_entries.append(industry_type)
        
        for value in indian_cities.values():
            for state in value:
                if state["name"] not in states:
                    for city in state["cities"]:
                        value = {    
                            "city": city["name"],
                            "state": state["name"],
                            "country": "Indian"
                        }
                        location = cls(value=value,type="location")
                        location.create(session=session)
                        new_entries.append(location)

        if new_entries:
            session.commit() 


    @classmethod
    def add_default_department_names(cls, session: Session):
        # inserting default department names 
        department_exists = session.query(cls).filter_by(type='department').all()
        names = {entry.value['name'] for entry in department_exists if 'name' in entry.value}

        department_names = MasterData.get_default_department_names()
        new_entries = []
        for department in department_names:
            if department not in names:
                department = cls(value={"name": department}, type="department")
                department.create(session=session)
                new_entries.append(department)
                
        if new_entries:
            session.commit() 

    @classmethod
    def insert_default_designations(cls, session: Session):
        """
        Add default designations to the database.
        """
        current_dir = os.path.dirname(__file__)
        designations_json_file = os.path.join(current_dir, '..', 'datasets', 'designations_names.json')

        with open(designations_json_file, mode='r') as file:
            designations = json.load(file)

        # --- Fetch all existing designations ---
        existing_designations = set(
            (row.value["title"], row.value["domain"])
            for row in session.query(MasterData)
            .filter(MasterData.type == "designation")
            .all()
        )

        # --- Insert only new records ---
        for domain, titles in designations["domains"].items():
            for title in titles:
                key = (title, domain)
                if key not in existing_designations:
                    record = MasterData(
                        value={"title": title, "domain": domain},
                        type="designation"
                    )
                    session.add(record)

        # --- Commit and close ---
        session.commit()
        session.close()

    @classmethod
    def insert_default_job_titles(cls, session: Session):
        """
        insert default job titles to the database.
        """
        current_dir = os.path.dirname(__file__)
        job_titles_json_file = os.path.join(current_dir, '..', 'datasets', 'job_titles.json')

        with open(job_titles_json_file, mode='r') as file:
            job_titles = json.load(file)

        # --- Fetch all existing job titles ---
        existing_designations = set(
            row.value["name"]
            for row in session.query(cls)
            .filter(cls.type == "job title")
            .all()
        )

        for job_title in job_titles:
            if job_title not in existing_designations:
                record = MasterData(
                    value={"name": job_title},
                    type="job title"
                )
                session.add(record) 

        # --- Commit and close ---
        session.commit()
        session.close()

    @staticmethod
    def get_default_department_names():
        department_names = [
            "Software Development",
            "IT Support",
            "Human Resources",
            "Sales & Marketing",
            "Finance & Accounting",
            "Customer Support",
            "Operations",
            "Product Management",
            "Business Development",
            "Supply Chain & Logistics",
            "Quality Assurance",
            "Legal & Compliance",
            "Other"
            ]
        return department_names