from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, Dict
from datetime import datetime
import pytz 
import re
from app.utils.validators import has_proper_characters, is_non_empty, validate_length

class InterviewDetails(BaseModel):
    recruiter_id: str = Field(..., title="Recruiter ID")
    applicant_id: str = Field(..., title="Applicant ID")
    interview_type: str = Field(..., title="Interview Type")
    platform: str = Field(..., title="Platform")
    date: str = Field(..., title="Date")
    start_time: str = Field(..., title="Start Time")
    end_time: str = Field(..., title="End Time")
    timezone: str = Field(..., title="Time Zone")
    interview_title: str = Field(..., title="Interview Title")
    interviewer_email: EmailStr = Field(..., title="Interviewer Email")
    applicant_email: EmailStr = Field(..., title="Applicant Email")
    description: str = Field(..., title="Description")
    additional_details: Optional[Dict[str, str]] = Field(default=None, title="Additional Details")

    @field_validator("date")
    def validate_date(cls, date):
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in the format YYYY-MM-DD")
        return date

    @field_validator("start_time", "end_time")
    def validate_time(cls, time):
        if not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", time):
            raise ValueError("Time must be in the format HH:MM")
        return time

    @field_validator("timezone")
    def validate_timezone(cls, timezone):
        if timezone not in pytz.all_timezones:
            raise ValueError("Invalid timezone")
        return timezone

    @field_validator("interviewer_email", "applicant_email")
    def validate_email(cls, email):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email address")
        return email


    @field_validator("description")
    def validate_description(cls, description):
        is_non_empty(value=description, field_name="Description")
        has_proper_characters(value=description, field_name="Description")
        return validate_length(value=description, min_len=0, max_len=250, field_name="Description")

# Example usage:
interview = InterviewDetails(
    recruiter_id="12345",
    applicant_id="67890",
    interview_type="Technical",
    platform="Microsoft Teams",
    date="2025-03-10",
    start_time="14:00",
    end_time="15:00",
    timezone="Asia/Kolkata",
    interview_title="Software Engineer Interview",
    interviewer_email="interviewer@example.com",
    applicant_email="applicant@example.com",
    description="Technical interview focusing on software engineering skills.",
    additional_details={"note": "Please be prepared with your portfolio."}
)
