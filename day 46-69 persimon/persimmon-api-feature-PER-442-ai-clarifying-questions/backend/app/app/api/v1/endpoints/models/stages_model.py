from pydantic import BaseModel
from uuid import UUID

class StageModel(BaseModel):
    uuid: UUID
    name: str

class StagesPartialUpdate(BaseModel):
    stages: list[StageModel]