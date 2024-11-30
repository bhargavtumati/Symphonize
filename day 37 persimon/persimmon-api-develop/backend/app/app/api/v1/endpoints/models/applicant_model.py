from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from sqlalchemy.dialects.postgresql import JSONB


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
    applicant_uuids: list[str]
    stage_uuid: str


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
    value: Optional[int]=None


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
    filters: Filters

