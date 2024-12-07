from pydantic import BaseModel, Field, field_validator, model_validator
from app.utils.validators import (
    validate_letters_and_numbers,
    is_non_empty,
    validate_length,
    validate_numeric_range,
    has_proper_characters,
    validate_job_location,
)
from app.api.v1.endpoints.models.company_model import CompanyModel
from typing import Optional, List
from app.models.job import JobStatusTypeEnum, JobTypeEnum, WorkplaceTypeEnum
from datetime import datetime

JOB_TITLE_FIELD = "Job title"
JOB_DESCRIPTION_FIELD = "Job description"
MINIMUM_EXPERIENCE_FIELD = "Minimum experience"
MAXIMUM_EXPERIENCE_FIELD = "Maximum experience"
MINIMUM_SALARY_FIELD = "Minimum salary"
MAXIMUM_SALARY_FIELD = "Maximum salary"


class QuestionAnswerDict(BaseModel):
    question: str
    answer: str


class JobModel(BaseModel):
    title: str
    type: JobTypeEnum
    status: JobStatusTypeEnum
    workplace_type: WorkplaceTypeEnum
    location: str
    team_size: str
    min_salary: float
    max_salary: float
    min_experience: int
    max_experience: int
    target_date: datetime
    description: str
    is_posted_for_client: bool
    company: CompanyModel
    ai_clarifying_questions: Optional[List[QuestionAnswerDict]] = Field(
        default_factory=list
    )
    publish_on_career_page: Optional[bool] = True
    publish_on_job_boards: Optional[List[str]] = Field(default_factory=list)

    @field_validator("title")
    def validate_title(cls, title):
        is_non_empty(value=title, field_name=JOB_TITLE_FIELD)
        has_proper_characters(value=title, field_name=JOB_TITLE_FIELD)
        validate_letters_and_numbers(value=title, field_name=JOB_TITLE_FIELD)
        return validate_length(
            value=title, min_len=3, max_len=50, field_name=JOB_TITLE_FIELD
        )

    @field_validator("description")
    def validate_description(cls, description):
        is_non_empty(value=description, field_name=JOB_DESCRIPTION_FIELD)
        if len(description) < 50:
            raise ValueError(
                f"${JOB_DESCRIPTION_FIELD} is too short. Please add more details"
            )
        if len(description) > 2000:
            raise ValueError(
                f"${JOB_DESCRIPTION_FIELD} is too long. Please limit it to 2000 characters"
            )
        return description

    @field_validator("team_size")
    def validate_team_size(cls, team_size):
        valid_sizes = ["1-5", "6-10", "11-20", "21-50", "51-100", "101-200", "201+"]

        if team_size not in valid_sizes:
            raise ValueError(f"Team size must be one of {', '.join(valid_sizes)}")
        return team_size

    @field_validator("min_experience")
    def validate_min_experience(cls, min_experience):
        return validate_numeric_range(
            value=min_experience,
            min_val=1,
            max_val=49,
            field_name=MINIMUM_EXPERIENCE_FIELD,
        )

    @field_validator("max_experience")
    def validate_max_experience(cls, max_experience):
        return validate_numeric_range(
            value=max_experience,
            min_val=2,
            max_val=50,
            field_name=MAXIMUM_EXPERIENCE_FIELD,
        )

    @field_validator("min_salary")
    def validate_min_salary(cls, min_salary):
        return validate_numeric_range(
            value=min_salary, min_val=1, max_val=99, field_name=MINIMUM_SALARY_FIELD
        )

    @field_validator("max_salary")
    def validate_max_salary(cls, max_salary):
        return validate_numeric_range(
            value=max_salary, min_val=2, max_val=100, field_name=MAXIMUM_SALARY_FIELD
        )

    @field_validator("location")
    def validate_location(cls, location):
        return validate_job_location(location=location)

    @model_validator(mode="after")
    def check_experience_range(cls, values):
        min_experience = values.min_experience
        max_experience = values.max_experience
        min_salary = values.min_salary
        max_salary = values.max_salary

        if min_experience >= max_experience:
            raise ValueError(
                "Minimum experience cannot be greater than or equal to maximum experience"
            )

        if min_salary >= max_salary:
            raise ValueError(
                "Minimum salary cannot be greater than or equal to maximum salary"
            )

        return values


class JobPartialUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[JobTypeEnum] = None
    status: Optional[JobStatusTypeEnum] = None
    workplace_type: Optional[WorkplaceTypeEnum] = None
    location: Optional[str] = None
    team_size: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    target_date: Optional[datetime] = None
    description: Optional[str] = None
    is_posted_for_client: Optional[bool] = None
    company: Optional[CompanyModel] = None
    ai_clarifying_questions: Optional[List[QuestionAnswerDict]] = Field(
        default_factory=list
    )
    publish_on_career_page: Optional[bool] = None
    publish_on_job_boards: Optional[List[str]] = Field(default_factory=list)
