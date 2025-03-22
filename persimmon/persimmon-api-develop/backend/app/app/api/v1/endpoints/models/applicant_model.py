from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator, model_validator
from typing import Any, Optional, List,Dict,Union
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID
from app.utils.validators import (
    is_non_empty, validate_email_address, validate_length, validate_linkedin_url, 
    validate_mobile_number, validate_name_with_fullstop, validate_Preference,
    validate_numeric_range, validate_industry_type, validate_job_location, get_education_institutions_list)
from datetime import datetime
from zoneinfo import available_timezones
from enum import Enum


class SocialMedia(BaseModel):
    github: Optional[str] = ""
    facebook: Optional[str] = ""
    linkedin: Optional[str] = ""
    instagram: Optional[str] = ""


class JobInformation(BaseModel):
    skills: Optional[List[str]] = []
    job_title: Optional[str] = ""
    department: Optional[str] = ""
    current_ctc: Optional[Union[float,str]] = None 
    expected_ctc: Optional[Union[float,str]] = None
    job_location: Optional[str] = ""
    current_work_at: Optional[str] = ""
    work_experience: Optional[Any] = ""


class PersonalInformation(BaseModel):
    email: Optional[str] = ""
    phone: Optional[str] = ""
    gender: Optional[str] = ""
    address: Optional[str] = ""
    full_name: Optional[str] = ""
    date_of_birth: Optional[str] = ""


class ApplicantDetails(BaseModel):
    about: Optional[str] = ""
    social_media: Optional[SocialMedia] = SocialMedia()
    original_resume: Optional[str] = ""
    job_information: Optional[JobInformation] = JobInformation()
    processed_resume: Optional[str] = ""
    personal_information: Optional[PersonalInformation] = PersonalInformation()
    
class ApplicantDetailsPartialUpdate(BaseModel):
    about: Optional[str] = ""
    social_media: Optional[SocialMedia] = SocialMedia()
    original_resume: Optional[str] = ""
    job_information: Optional[JobInformation] = JobInformation()
    processed_resume: Optional[str] = ""
    personal_information: Optional[PersonalInformation] = PersonalInformation()
    model_config = ConfigDict(extra='ignore')


class ApplicantPartialUpdate(BaseModel):
    applicant_uuids: list[UUID]
    stage_uuid: UUID


# Model for Industry Type
class IndustryType(BaseModel):
    name: Optional[str]=None
    pref: Optional[str]=None
    max: Optional[float]=None
    min: Optional[float]=None

    @field_validator('name')
    def validate_name(cls, name):
        validate_industry_type(name)
        return name

    @field_validator('pref')
    def validate_pref(cls, pref):
        validate_Preference(pref)
        return pref
    
    @field_validator('min')
    def validate_min(cls, min: int):
        validate_numeric_range(min, 1, 49, "min")
        return min
    
    @field_validator('max')
    def validate_max(cls, max: int):
        validate_numeric_range(max, 2, 50, "max")
        return max
    
    @model_validator(mode="after")
    def validate_min_less_than_max(self):
        if self.min >= self.max:
            raise ValueError("min must be less than max.")
        return self
    

# Model for Remuneration
class Remuneration(BaseModel):
    name: Optional[str]=None
    max: Optional[float]=None
    min: Optional[float]=None

    @field_validator('name')
    def validate_name(cls, name: str):
        if name.lower() not in ['salary range', '']:
            raise ValueError("name must be 'Salary Range'")
        return name

    @model_validator(mode="after")
    def validate_min_and_max(self):
        if self.name:
            validate_numeric_range(self.max, 2, 100, "max")
            validate_numeric_range(self.min, 1, 99, "min")
            if self.min >= self.max:
                raise ValueError("min must be less than max.")
            return self

    
# Model for Skills and Soft Skills
class Skill(BaseModel):
    name: Optional[str]=None
    pref: Optional[str]=None
    value: Optional[int]=None

    # @field_validator('pref')
    @classmethod
    def validate_pref(cls, pref: str):
        validate_Preference(pref)
        return pref
    
    # @field_validator('value')
    @classmethod
    def validate_value(cls, value): 
        validate_numeric_range(value, 0, 10, "value")
        return value
    
    @model_validator(mode="after")
    def validate_skills(self):
        if self.name:
            Skill.validate_pref(self.pref)
            Skill.validate_value(self.value)
        return self


class SoftSkill(BaseModel):
    name: Optional[str]=None
    pref: Optional[str]=None
    min_value: Optional[str]=None
    max_value: Optional[str]=None

    # @field_validator('pref')
    @classmethod
    def validate_pref(cls, pref: str):
        validate_Preference(pref)
        return pref

    @model_validator(mode="after")
    def validate_min_and_max(self):
        if not self.name :
            return self
        SoftSkill.validate_pref(self.pref)
        # if f"{self.min_value}-{self.max_value}" not in ["0-4", "4-7", "8-10"]:
        #     raise ValueError(
        #         f"Invalid range: {self.min_value}-{self.max_value}. "
        #         "Please enter a valid range. Allowed ranges are: 0-4, 4-7, or 8-10."
        #     )
        return self


# Model for Responsibilities
class Responsibilities(BaseModel):
    responsibilities: Optional[List[str]] = None


# Model for Pedigree Specifications
class Specification(BaseModel):
    spec: Optional[str]=None
    qualification: Optional[str]=None
    institution_name: Optional[str]=None

    # @field_validator('spec')
    @classmethod
    def validate_spec(cls, spec: str):
        if spec.lower() not in ["exclude", "include"]:
            raise ValueError("spec must be either 'Exclude' or 'Include'")
        return spec


# Model for Pedigree
class Pedigree(BaseModel):
    name: Optional[str]=None
    specifications: Optional[List[Specification]] = None

    # @field_validator('name')
    @classmethod
    def validate_name(cls, name: str):
        if name.lower() not in ["education", "company"]:
            raise ValueError("name must be either 'education' or 'company'")
        return name
    
    @model_validator(mode="after")
    def validate_specifications(self):
        if not self.name:
            return self
        Pedigree.validate_name(self.name)
        RULES = {
            "education": {
                "qualifications": {"class 10", "class 12", "diploma", "degree", "b.tech", "m.tech", "phd", "post graduate"},
                "institutions": get_education_institutions_list() # {"University of Example", "Example State University", "Technical Institute", "Community College"},
            },
            "company": {
                "qualifications": {"example corp", "tech solutions", "global industries", "innovation ltd"},
                "institutions": {"Technology", "Healthcare", "Finance", "Education", "Manufacturing"}
            }
        }
        for spec in self.specifications:
            Specification.validate_spec(spec.spec)
            if spec.qualification.strip().lower() not in RULES[self.name]["qualifications"]:
                raise ValueError("Please enter a valid qualification")
            if spec.institution_name not in RULES[self.name]["institutions"]:
                raise ValueError("Please enter a valid institution name")
        return self


# Model for Availability
class Availability(BaseModel):
    name: Optional[str]=None
    value: Optional[int]=None

    @field_validator('name')
    def validate_name(cls, name: str):
        print("the validation is ",name)
        if name.lower() not in ["can join in", ""]:
            raise ValueError("name must be 'Can Join in'")
        return name
        
    @field_validator('value')
    def validate_value(cls, value):
        if not (0 <= value <= 99):
            raise ValueError("value must be within the range 0 to 99")
        return value


# Model for Work Mode
class WorkMode(BaseModel):
    value: Optional[str]=None

    @field_validator('value')
    def validate_value(cls, value: str):
        valid_work_modes = {"any", "work from home", "hybrid", "work from office", ""}
        if value.lower() not in valid_work_modes:
            raise ValueError(
                "value must be one of: 'ANY', 'Work From Home', 'Hybrid', or 'Work From Office'."
            )
        return value


# Model for Location
class Location(BaseModel):
    first_priority: Optional[str]=None
    second_priority: Optional[str]=None

    @field_validator('first_priority')
    def validate_first_priority(cls, first_priority: str):
        if not first_priority:
            return first_priority
        if first_priority.lower() == "any":
            return first_priority
        validate_job_location(first_priority)
        return first_priority


# Model for Transition Behavior
class TransitionBehaviour(BaseModel):
    name: Optional[str]=None
    preference: Optional[str]=None
    value: Optional[int]=None

    @field_validator('name')
    def validate_name(cls, name: str):
        if name.lower() not in  ["avg. duration in previous companies", ""]:
            raise ValueError("name must be 'Avg. Duration in Previous Companies'")  
        return name
    
    @model_validator(mode="after")
    def validate_preference(self):
        if self.name:
            validate_Preference(self.preference)
        return self
    
    @field_validator('value')
    def validate_value(cls, value):
        validate_numeric_range(value, 0, 50, "value")
        return value


# Model for Advanced Filters
class AdvancedFilter(BaseModel):
    name: Optional[str]=None
    preference: Optional[str]=None
    value: Optional[str]=None

    @field_validator('name')
    def validate_name(cls, name: str):
        if name.lower() not in ["team size", "company size", ""]:
            raise ValueError("name must be either 'team size' or 'company size'")  
        return name

    # @field_validator('preference')
    @classmethod
    def validate_pref(cls, preference: str):
        validate_Preference(preference)
        return preference

    @model_validator(mode="after")
    def validate_value(self):
        if self.name:
            AdvancedFilter.validate_pref(self.preference)
            if self.name == "team size":
                if self.value not in ["1-5", "6-10", "11-20", "21-50", "51-100", "101-200", "200+"]:
                    raise ValueError("Please enter a valid value")
            else:
                if self.value not in ["1-10", "11-50", "51-200", "201-500", "501-1000", "1001-5000", "5001-10000", "10000+"]:
                    raise ValueError("Please enter a valid value")
        return self


# Main Filters Model
class Filters(BaseModel):
    industry_type: Optional[List[IndustryType]]  =None 
    remuneration: Optional[Remuneration]  =None
    skills: Optional[List[Skill]] =None
    responsibilities: Optional[List[str]] =None
    pedigree: Optional[List[Pedigree]] =None
    availability: Optional[Availability] =None
    workmode: Optional[WorkMode] =None
    location: Optional[Location] =None
    soft_skills: Optional[List[SoftSkill]] =None
    transition_behaviour: Optional[List[TransitionBehaviour]] =None
    advanced_filters: Optional[List[AdvancedFilter]] =None

    # @field_validator('responsibilities')
    # def validate_responsibilities_count(cls, responsibilities):
    #     if len(responsibilities)>20:
    #         raise ValueError("responsibilities must not be greater than 20")
    #     return responsibilities
    
    # @field_validator('skills')
    # def validate_skills_count(cls, skills):
    #     if len(skills)>10:
    #         raise ValueError("skills must not be greater than 10")
    #     return skills
    
    # @field_validator('soft_skills')
    # def validate_softskills_count(cls, soft_skills):
    #     if len(soft_skills)>10:
    #         raise ValueError("soft_skills must not be greater than 10")
    #     return soft_skills


# Root Model
class FilterRequest(BaseModel):
    filters: Optional[Filters] = None


class ResumeFlatten(BaseModel):
    data:Dict


class TextRequest(BaseModel):
    text: str

# Main request body
class ApplicantRequest(BaseModel):
    details: Dict

class PayloadModel(BaseModel):
    data: Dict

# Define the Pydantic model
class Message(BaseModel):
    data: dict

allowed_domains_for_applicant_email = [
    "gmail.com", "outlook.com", "yahoo.com", "icloud.com", "protonmail.com",
    "proton.me", "gmx.com", "mail.ru", "yandex.com", "yandex.ru", "zoho.com",
    "aol.com", "mail.com", "consultant.com", "teacher.com"
]

class ApplicantModel(BaseModel):
    phone_number: int
    full_name: str
    email_id: EmailStr
    linkedin_url: str

    @field_validator('phone_number')
    def validate_phone_number(cls, phone_number):
        validate_mobile_number(phone_number, "phone number")
        return phone_number

    @field_validator('full_name')
    def validate_full_name(cls, full_name):
        is_non_empty(full_name, "Full Name")
        validate_name_with_fullstop(full_name, "Full Name")
        return full_name

    @field_validator('linkedin_url')
    def validate_linkedin(cls, linkedin_url):
        validate_linkedin_url(linkedin_url)
        return linkedin_url

    @field_validator('email_id')
    def validate_email(cls, email_id):
        validate_email_address(email_id, allowed_domains_for_applicant_email, "Email Id")
        return email_id


class MeetingInvite(BaseModel):
    email: EmailStr

class Settings(BaseModel):
    meeting_authentication: Optional[bool] = None
    meeting_invitees: List[MeetingInvite]
    push_change_to_calendar: Optional[bool] = None
    
class MeetingModel(BaseModel):
    agenda: str
    duration: Optional[int] = None
    schedule_for: Optional[EmailStr] = None
    allow_multiple_devices: Optional[bool] = None
    settings: Settings
    start_time: datetime
    timezone: Optional[str] = None
    topic: str

    @field_validator("timezone")
    def validate_timezone(cls, value):
        if value not in available_timezones():
            raise ValueError(f"Invalid timezone: {value}")
        return value

    @field_validator("agenda")
    def validate_agenda(cls, value):
        is_non_empty(value, "Description")
        return value

    @field_validator("topic")
    def validate_topic(cls, value):
        is_non_empty(value, "Title")
        return value


# Enum for opinion choices
class OpinionEnum(str, Enum):
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"

# Rating model with constraints using Field()
class Rating(BaseModel):
    skill: int = Field(..., ge=1, le=5)  # Rating between 0 and 10
    communication: int = Field(..., ge=1, le=5)
    professionalism: int = Field(..., ge=1, le=5)


ALLOWED_CHARACTERS = set(". , ? ! : ; ' - \" () {} [] <> _ - & @ / \\")


# Feedback item model
class FeedbackItem(BaseModel):
    rating: Rating
    overall_feedback: str
    opinion: Optional[OpinionEnum] = None
    given_by: EmailStr  

    @field_validator('overall_feedback')
    def validate_overall_feedback(cls, overall_feedback):
        if not all(char.isalnum() or char.isspace() or char in ALLOWED_CHARACTERS for char in overall_feedback):
            raise ValueError("overall_feedback must not contain special characters")
        overall_feedback = overall_feedback.strip()
        if len(overall_feedback)<50 or len(overall_feedback)>1000:
            raise ValueError("overall_feedback must be between 50 and 1000 characters")
        return overall_feedback

# Main payload model
class FeedbackPayload(BaseModel):
    feedback: List[FeedbackItem] #using the list item to allow multiple feedback in database jsonb column
    
    @field_validator('feedback')
    def validate_feedback(cls, feedback):
        if len(feedback) == 0:
            raise ValueError("feedback must not be empty")
        return feedback

class ShareRequest(BaseModel):
    job_code: str
    sender: EmailStr
    email_type: str
    recipient_emails: List[EmailStr]
    applicant_uuids: List[str] 
    hide_salary: bool  = False
    redirect_url: str

    @field_validator('email_type')
    def validate_email_type(cls, email_type):
        if email_type not in ['default', 'brevo', 'sendgrid']:
            raise ValueError("Invalid email_type. Allowed values are 'default', 'brevo' and 'sendgrid'")
        return email_type    
    
    @field_validator('recipient_emails')
    def validate_recipient_emails(cls, recipient_emails):
        if len(recipient_emails) == 0:
            raise ValueError("recipient_emails must me atleast one")
        return recipient_emails

    @field_validator('applicant_uuids')
    def validate_applicant_uuids(cls, applicant_uuids):
        if len(applicant_uuids) == 0:
            raise ValueError("applicant_uuids must me atleast one")
        return applicant_uuids
