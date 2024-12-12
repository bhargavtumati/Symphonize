from pydantic import BaseModel

class QuestionAnswerDict(BaseModel):
    question: str
    answer: str