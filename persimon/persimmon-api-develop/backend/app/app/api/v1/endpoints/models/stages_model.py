from pydantic import BaseModel, field_validator
from uuid import UUID
from app.utils.validators import validate_length
import re

STAGE_NAME_FIELD = "Stage name"

class StageModel(BaseModel):
    uuid: UUID
    name: str

    @field_validator("name")
    def validate_name(cls, name):
        validate_length(value=name, min_len=3, max_len=30, field_name=STAGE_NAME_FIELD)
        if not re.fullmatch(r"[A-Za-z0-9\s-]+", name):
            raise ValueError("Stage names can only be Alphabets or Alphanumeric values")
        if name.startswith(" ") or name.endswith(" ") or name.startswith("-") or name.endswith("-"):
            raise ValueError("Please enter a valid name")
        if "  " in name or "--" in name:
            raise ValueError("Please enter a valid name")
        return name

class StagesPartialUpdate(BaseModel):
    stages: list[StageModel]