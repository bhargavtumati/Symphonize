from pydantic import BaseModel, Field, field_validator, EmailStr
import re
from app.api.v1.endpoints.models.company_model import CompanyModel
from app.utils.validators import is_alphabetic, is_non_empty, validate_linkedin_url, validate_professional_email, validate_whatsapp_number, validate_length, has_proper_characters 

FULL_NAME_FIELD = "Full Name"
DESIGNATION_FIELD = "Designation"

class RecruiterModel(BaseModel):
    full_name: str
    whatsapp_number: str
    designation: str
    linkedin_url: str
    email_id: EmailStr
    company: CompanyModel

    @field_validator('full_name')
    def validate_full_name(cls, full_name):
        is_non_empty(full_name, FULL_NAME_FIELD)
        is_alphabetic(full_name, FULL_NAME_FIELD)
        has_proper_characters(full_name, FULL_NAME_FIELD)
        validate_length(full_name, 3, 20, FULL_NAME_FIELD)
        if ' ' not in full_name:
            raise ValueError("Please enter your Full name, in 'First name Last name' format.")
        return full_name

    @field_validator('whatsapp_number')
    def validate_whatsapp(cls, whatsapp_number):
        return validate_whatsapp_number(whatsapp_number)

    @field_validator('designation')
    def validate_designation(cls, designation):
        is_non_empty(designation, DESIGNATION_FIELD)
        is_alphabetic(designation, DESIGNATION_FIELD)
        has_proper_characters(designation, DESIGNATION_FIELD)
        return validate_length(designation, 2, 20, DESIGNATION_FIELD)

    @field_validator('linkedin_url')
    def validate_linkedin(cls, linkedin_url):
        return validate_linkedin_url(linkedin_url)

    @field_validator('email_id')
    def validate_email(cls, email_id):
        return validate_professional_email(email_id)