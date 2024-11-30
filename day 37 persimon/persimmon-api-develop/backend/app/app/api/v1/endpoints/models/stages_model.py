from pydantic import BaseModel

class StageModel(BaseModel):
    uuid: str
    name: str

class StagesPartialUpdate(BaseModel):
    stages: list[StageModel]