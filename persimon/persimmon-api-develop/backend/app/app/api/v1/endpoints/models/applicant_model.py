from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import Optional, List,Dict,Union
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID
from app.utils.validators import is_non_empty, validate_length, validate_linkedin_url, validate_email_address, validate_name_with_fullstop, validate_mobile_number

class SocialMedia(BaseModel):
    github: Optional[str] = ""
    facebook: Optional[str] = ""
    linkedin: Optional[str] = ""
    instagram: Optional[str] = ""


class JobInformation(BaseModel):
    skills: Optional[List[str]] = []
    job_title: Optional[str] = ""
    department: Optional[str] = ""
    current_ctc: Optional[str] = ""
    expected_ctc: Optional[str] = ""
    job_location: Optional[str] = ""
    current_work_at: Optional[str] = ""
    work_experience: Optional[str] = ""


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


class ApplicantPartialUpdate(BaseModel):
    applicant_uuids: list[UUID]
    stage_uuid: UUID


# Model for Industry Type
class IndustryType(BaseModel):
    name: Optional[str]=None
    pref: Optional[str]=None
    max: Optional[int]=None
    min: Optional[int]=None


# Model for Remuneration
class Remuneration(BaseModel):
    name: Optional[str]=None
    max: Optional[int]=None
    min: Optional[int]=None


# Model for Skills and Soft Skills
class Skill(BaseModel):
    name: Optional[str]=None
    pref: Optional[str]=None
    value: Optional[int]=None

class SoftSkill(BaseModel):
    name: Optional[str]=None
    pref: Optional[str]=None
    min_value: Optional[str]=None
    max_value: Optional[str]=None

# Model for Responsibilities
class Responsibilities(BaseModel):
    responsibilities: Optional[List[str]] = None


# Model for Pedigree Specifications
class Specification(BaseModel):
    spec: Optional[str]=None
    qualification: Optional[str]=None
    institution_name: Optional[str]=None


# Model for Pedigree
class Pedigree(BaseModel):
    name: Optional[str]=None
    specifications: Optional[List[Specification]] = None


# Model for Availability
class Availability(BaseModel):
    name: Optional[str]=None
    value: Optional[int]=None


# Model for Work Mode
class WorkMode(BaseModel):
    value: Optional[str]=None


# Model for Location
class Location(BaseModel):
    first_priority: Optional[str]=None
    second_priority: Optional[str]=None


# Model for Transition Behavior
class TransitionBehaviour(BaseModel):
    name: Optional[str]=None
    preference: Optional[str]=None
    value: Optional[int]=None


# Model for Advanced Filters
class AdvancedFilter(BaseModel):
    name: Optional[str]=None
    preference: Optional[str]=None
    value: Optional[str]=None


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
        validate_length(full_name, 3, 25, "Full Name")
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