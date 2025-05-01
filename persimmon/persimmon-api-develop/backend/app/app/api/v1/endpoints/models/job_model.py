from datetime import datetime
from decimal import Decimal
from typing import Any, Optional, List

import requests 

from pydantic import BaseModel, Field, field_validator, model_validator

from app.utils.validators import (
    validate_letters_and_numbers, 
    is_non_empty, validate_length, 
    validate_numeric_range, 
    has_proper_characters, 
    validate_job_location, 
    validate_decimal_point,
    validate_currency_code
)
from app.api.v1.endpoints.models.company_model import CompanyModel
from app.models.job import JobStatusTypeEnum, JobTypeEnum, WorkplaceTypeEnum
from app.api.v1.endpoints.models.common_models import QuestionAnswerDict

JOB_TITLE_FIELD = "Job title"
JOB_DESCRIPTION_FIELD = "Job description"
MINIMUM_EXPERIENCE_FIELD = "Minimum experience"
MAXIMUM_EXPERIENCE_FIELD = "Maximum experience"
MINIMUM_SALARY_FIELD = "Minimum salary"
MAXIMUM_SALARY_FIELD = "Maximum salary"

class JobModel(BaseModel):
    title: str
    type: JobTypeEnum
    status: JobStatusTypeEnum
    workplace_type: WorkplaceTypeEnum
    location: str
    team_size: str
    currency: str
    min_salary: int
    max_salary: int
    min_experience: float
    max_experience: float
    target_date: datetime
    description: str
    enhanced_description: dict
    is_posted_for_client: bool
    company: CompanyModel
    ai_clarifying_questions: Optional[List[QuestionAnswerDict]] = Field(default_factory=list)
    publish_on_career_page: Optional[bool] = True
    publish_on_job_boards: Optional[List[str]] = Field(default_factory=list)
    published_on_other_domains: Optional[bool] = False

    @field_validator("title")
    def validate_title(cls, title):
        is_non_empty(value=title, field_name=JOB_TITLE_FIELD)
        has_proper_characters(value=title, field_name=JOB_TITLE_FIELD)
        validate_letters_and_numbers(value=title, field_name=JOB_TITLE_FIELD)
        return validate_length(value=title, min_len=3, max_len=50, field_name=JOB_TITLE_FIELD)

    @field_validator("description")
    def validate_description(cls, description):
        is_non_empty(value=description, field_name=JOB_DESCRIPTION_FIELD)
        if len(description) < 3000:
            raise ValueError(f"{JOB_DESCRIPTION_FIELD} must contain a minimum of 3000 characters")
        return description
        
    @field_validator('team_size')
    def validate_team_size(cls, team_size):
        valid_sizes = [
            "1-5", "6-10", "11-20", "21-50",
            "51-100", "101-200", "201+"
        ]

        if team_size not in valid_sizes:
            raise ValueError(f"Team size must be one of {', '.join(valid_sizes)}")
        return team_size

    @field_validator('min_experience')
    def validate_min_experience(cls, min_experience):
        validate_decimal_point(value=min_experience)
        return validate_numeric_range(value=min_experience, min_val=1, max_val=49, field_name=MINIMUM_EXPERIENCE_FIELD)

    @field_validator('max_experience')
    def validate_max_experience(cls, max_experience):
        validate_decimal_point(value=max_experience)
        return validate_numeric_range(value=max_experience, min_val=2, max_val=50, field_name=MAXIMUM_EXPERIENCE_FIELD)
    
    @field_validator('currency')
    def validate_currency(cls, currency):
        return validate_currency_code(code=currency)

    @field_validator('min_salary')
    def validate_min_salary(cls, min_salary):
        if min_salary <= 0:
            raise ValueError("Minimum salary must be greater than 0")
        return min_salary
    
    @field_validator('max_salary')
    def validate_max_salary(cls, max_salary):
        if max_salary <= 0:
            raise ValueError("Maximum salary must be greater than 0")
        return max_salary
    
    @model_validator(mode='after')
    def validate_min_salary_and_max_salary(self):
        if self.min_salary >= self.max_salary:
            raise ValueError("Minimum salary cannot be greater than or equal to maximum salary")
        return self

    @field_validator('location')
    def validate_location(cls, location):
        return validate_job_location(location=location)

    @model_validator(mode='after')
    def check_experience_range(cls, values):
        min_experience = values.min_experience
        max_experience = values.max_experience
        min_salary = values.min_salary
        max_salary = values.max_salary
    
        if min_experience >= max_experience:
            raise ValueError("Minimum experience cannot be greater than or equal to maximum experience")

        if min_salary >= max_salary:
            raise ValueError("Minimum salary cannot be greater than or equal to maximum salary")

        return values

class JobPartialUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[JobTypeEnum] = None
    status: Optional[JobStatusTypeEnum] = None
    workplace_type: Optional[WorkplaceTypeEnum] = None
    location: Optional[str] = None
    team_size: Optional[str] = None
    currency: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    target_date: Optional[datetime] = None
    description: Optional[str] = None
    is_posted_for_client: Optional[bool] = None
    company: Optional[CompanyModel] = None
    ai_clarifying_questions: Optional[List[QuestionAnswerDict]] = Field(default_factory=list)
    publish_on_career_page: Optional[bool] = None
    publish_on_job_boards: Optional[List[str]] = Field(default_factory=list)

    @field_validator('currency')
    def validate_currency(cls, currency):
        return validate_currency_code(code=currency)

    @field_validator('min_salary')
    def validate_min_salary(cls, min_salary):
        if min_salary <= 0:
            raise ValueError("Minimum salary must be greater than 0")
        return min_salary
    
    @field_validator('max_salary')
    def validate_max_salary(cls, max_salary):
        if max_salary <= 0:
            raise ValueError("Maximum salary must be greater than 0")
        return max_salary
    
    @model_validator(mode='after')
    def validate_min_salary_and_max_salary(self):
        if self.min_salary and self.max_salary and self.min_salary >= self.max_salary:
            raise ValueError("Minimum salary cannot be greater than or equal to maximum salary")
        return self


class JobDescription(BaseModel):
    description: str

class JobResponse(BaseModel):
    message: str
    data: dict
    status: int