from typing import Optional

from pydantic import BaseModel, field_validator, EmailStr

from app.api.v1.endpoints.models.company_model import CompanyModel
from app.utils.validators import (
    is_alphabetic, is_non_empty, 
    validate_linkedin_url, 
    validate_professional_email, 
    validate_length, 
    has_proper_characters,
    validate_mobile_number_with_country_code,
    validate_designation
)

FULL_NAME_FIELD = "Full Name"
DESIGNATION_FIELD = "Designation"

class RecruiterModel(BaseModel):
    full_name: str
    whatsapp_number: str
    designation: str
    linkedin_url: str
    email_id: EmailStr
    gmail_id: Optional[EmailStr] = None
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
        return validate_mobile_number_with_country_code(whatsapp_number, "WhatsApp Number")

    @field_validator('designation')
    def validate_designation(cls, designation):
        is_non_empty(designation, DESIGNATION_FIELD)
        validate_designation(designation)
        return designation

    @field_validator('linkedin_url')
    def validate_linkedin(cls, linkedin_url):
        return validate_linkedin_url(linkedin_url)

    @field_validator('email_id')
    def validate_email(cls, email_id):
        return validate_professional_email(email_id)
    

class UpdateRecruiterModel(BaseModel):
    full_name: Optional[str] = None
    whatsapp_number: Optional[str] = None
    designation: Optional[str] = None
    linkedin_url: Optional[str] = None

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
        return validate_mobile_number_with_country_code(whatsapp_number, "WhatsApp Number")

    @field_validator('designation')
    def validate_designation(cls, designation):
        is_non_empty(designation, DESIGNATION_FIELD)
        validate_designation(designation)
        return designation

    @field_validator('linkedin_url')
    def validate_linkedin(cls, linkedin_url):
        return validate_linkedin_url(linkedin_url)