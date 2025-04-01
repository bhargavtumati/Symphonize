import re
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator, model_validator
from typing import Any, Optional, List,Dict,Union
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID
from app.utils.validators import (
    has_proper_characters, is_alphabetic, is_non_empty, validate_decimal_point, validate_email_address, validate_facebook_url, validate_github_url, validate_instagram_url, validate_length, validate_letters_and_numbers, validate_linkedin_url, 
    validate_mobile_number, validate_name_with_fullstop, validate_Preference,
    validate_numeric_range, validate_industry_type, validate_job_location, get_education_institutions_list)
from datetime import datetime
from zoneinfo import available_timezones
from enum import Enum

FULL_NAME_FIELD = "Full Name"
JOB_TITLE_FIELD = "Job title"
CURRENT_CTC_FIELD = "Current salary"
EXPECTED_CTC_FIELD = "Expected salary"


class SocialMedia(BaseModel):
    github: Optional[str] = ""
    facebook: Optional[str] = ""
    linkedin: Optional[str] = ""
    instagram: Optional[str] = ""

    @field_validator('linkedin')
    def validate_linkedin(cls, linkedin):
        return validate_linkedin_url(linkedin)
    
    @field_validator('github')
    def validate_github(cls, github):
        return validate_github_url(github)
    
    @field_validator('facebook')
    def validate_facebook(cls, facebook):
        return validate_facebook_url(facebook)
    
    @field_validator('instagram')
    def validate_instagram(cls, instagram):
        return validate_instagram_url(instagram)


class JobInformation(BaseModel):
    skills: Optional[List[str]] = []
    job_title: Optional[str] = ""
    department: Optional[str] = ""
    current_ctc: Optional[Union[float,str]] = None 
    expected_ctc: Optional[Union[float,str]] = None
    job_location: Optional[str] = ""
    preferred_job_location: Optional[str] = ""
    current_work_at: Optional[str] = ""
    work_experience: Optional[str] = None

    @field_validator('job_title')
    def validate_title(cls, job_title):
        is_non_empty(value=job_title, field_name=JOB_TITLE_FIELD)
        has_proper_characters(value=job_title, field_name=JOB_TITLE_FIELD)
        validate_letters_and_numbers(value=job_title, field_name=JOB_TITLE_FIELD)
        return validate_length(value=job_title, min_len=3, max_len=50, field_name=JOB_TITLE_FIELD)
    
    @field_validator('work_experience')
    def validate_experience(cls, value):
        pattern = r"^(?P<years>\d{1,2}) Years (?P<months>\d{1,2}) Months$"
        match = re.match(pattern, value)
        
        if not match:
            raise ValueError("Invalid format. Use 'X Years Y Months' (e.g., '3 Years 7 Months').")

        years, months = int(match.group("years")), int(match.group("months"))
        if not (0 <= years <= 50):
            raise ValueError("Years must be between 0 and 50.")
        
        if not (0 <= months <= 11):
            raise ValueError("Months must be between 0 and 11.")

        return value
    
    @field_validator('job_location')
    def validate_location(cls, job_location):
        return validate_job_location(location=job_location)
    
    @field_validator('preferred_job_location')
    def validate_preferred_location(cls, preferred_job_location):
        return validate_job_location(location=preferred_job_location)
    

    @field_validator('current_ctc')
    def validate_current_ctc(cls, current_ctc):
        validate_decimal_point(value=current_ctc)
        return validate_numeric_range(value=current_ctc, min_val=2, max_val=100, field_name=CURRENT_CTC_FIELD) 
    
    @field_validator('expected_ctc')
    def validate_expected_ctc(cls, expected_ctc):
        validate_decimal_point(value=expected_ctc)
        return validate_numeric_range(value=expected_ctc, min_val=2, max_val=100, field_name=EXPECTED_CTC_FIELD) 
    

    @model_validator(mode='after')
    def check_salary_range(cls, values):
        current_ctc = values.current_ctc
        expected_ctc = values.expected_ctc
        
        if current_ctc and expected_ctc and current_ctc >= expected_ctc:
            raise ValueError("Minimum salary cannot be greater than or equal to maximum salary")

        return values
    
class PersonalInformation(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = ""
    gender: Optional[str] = ""
    address: Optional[str] = ""
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = ""

    @field_validator('full_name')
    def validate_full_name(cls, full_name):
        is_non_empty(full_name, FULL_NAME_FIELD)
        is_alphabetic(full_name, FULL_NAME_FIELD)
        has_proper_characters(full_name, FULL_NAME_FIELD)
        validate_length(full_name, 3, 20, FULL_NAME_FIELD)
        if ' ' not in full_name:
            raise ValueError("Please enter your Full name, in 'First name Last name' format.")
        return full_name
    
    @field_validator('gender')
    def validate_gender(cls, gender):
        if gender not in ['Male', 'Female', 'Non-Binary' ,'Prefer Not to Say']:
            raise ValueError("Gender should be either 'Male' or 'Female' or 'Non-Binary' or'Prefer Not to Say'.")
        return gender
    
    @field_validator('date_of_birth')
    def validate_date_of_birth(cls, date_of_birth):
        if not re.match(r"^\d{2}-\d{2}-\d{4}$", date_of_birth):
            raise ValueError("Date of birth should be in the format dd-mm-yyyy.")
        return date_of_birth
    
    @field_validator('address')
    def validate_address_field(cls, address):
        validate_length(address, 0, 300, "Address")
        if not re.match(r"^[a-zA-Z0-9 .,\-#/()\s]+$", address):
            raise ValueError("Only letters, numbers, spaces, and common special characters (.,-#/()) are allowed.")
        return address
    
    @field_validator('email')
    def validate_email(cls,email):
        allowed_pattern = r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(allowed_pattern, email):
            raise ValueError("Invalid email format. Only letters, numbers, dot, underscore, and hyphen are allowed before '@'.")
        return email



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

    @field_validator('about')
    def validate_about(cls, about):
        validate_length(about,min_len=0, max_len=1000, field_name="about") #check once more . 
        if not re.match(r"^[a-zA-Z0-9 ,.\-’]+$", about):
            raise ValueError("Only alphanumeric characters, spaces, and , . - ’ are allowed.")
        return about


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
            raise ValueError("""overall_feedback must only contain these special characters . , ? ! : ; ' - " () {} [] <> _ - & @ / \ """)
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
