from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy import Integer, String, exists, func
from sqlalchemy.dialects.postgresql import JSONB
from typing import List
from app.db.session import SessionLocal
import os
import json

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
    
    def create(self, session: Session):
        session.add(self)

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
