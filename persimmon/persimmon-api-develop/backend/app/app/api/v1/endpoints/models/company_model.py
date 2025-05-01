import re
from typing import Optional

from pydantic import BaseModel, field_validator

from app.utils.validators import(
    is_non_empty, 
    has_proper_characters, 
    validate_length, 
    validate_industry_type, 
    validate_facebook_url, 
    validate_twitter_url, 
    validate_instagram_url,
    validate_linkedin_company_url, 
)
from app.models.company import CompanyTypeEnum, BusinessTypeEnum


COMPANY_NAME_FIELD = "Company name"
COMPANY_WEBSITE_FIELD = "Website"
COMPANY_LINKEDIN_FIELD = "Company LinkedIn"
COMPANY_INSTAGRAM_FIELD = "Company Instagram"
COMPANY_FACEBOOK_FIELD = "Company Facebook"
COMPANY_TWITTER_FIELD = "Company Twitter"
COMPANY_ABOUT_FIELD = "About"

class CompanyModel(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    number_of_employees: Optional[str] = None
    industry_type: Optional[str] = None
    linkedin: Optional[str] = None
    type: Optional[CompanyTypeEnum] = None
    business_type: Optional[BusinessTypeEnum] = None
    about: Optional[str] = None
    tagline: Optional[str] = None
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    instagram: Optional[str] = None

    @field_validator('name')
    def validate_name(cls, name):
        is_non_empty(value=name, field_name=COMPANY_NAME_FIELD)
        has_proper_characters(value=name, field_name=COMPANY_NAME_FIELD)
        validate_length(value=name, min_len=3, max_len=50, field_name=COMPANY_NAME_FIELD)
        if not re.match(r'^[a-zA-Z0-9&\-\.\'\s]+$', name):
            raise ValueError("Company name can only contain alphanumeric characters, spaces, &, -, ., and '")
        return name

    @field_validator('website')
    def validate_website(cls, website: str) -> str:
        """
        Validates a company website URL based on the given rules.
        Rules:
        1. Must start with 'https://www.' or 'www.' or https://
        2. Company name must be at least 3 characters.
        3. Domain must be one of: .in, .com, .net, .org
        4. Total length must be between 10 and 100 characters.

        Returns:
            The validated website URL if valid, else raises a ValueError.
        """
        if not (10 <= len(website) <= 100):
            raise ValueError("Website URL must be between 10 and 100 characters.")
        pattern = r"^(https://www\.|www\.|https://)[a-zA-Z0-9-]{3,}\.(in|com|net|org)$"
        if not re.match(pattern, website):
            raise ValueError("Invalid website format. Must start with 'https://www.' or 'www.' or https:// and end with .in, .com, .net, or .org.")
        return website

    @field_validator('linkedin')
    def validate_linkedin(cls, linkedin):
        is_non_empty(value=linkedin, field_name=COMPANY_LINKEDIN_FIELD)
        validate_linkedin_company_url(value=linkedin)
        validate_length(value=linkedin, min_len=5, max_len=100, field_name=COMPANY_LINKEDIN_FIELD)
        return linkedin

    @field_validator('number_of_employees')
    def validate_size(cls, number_of_employees):
        valid_sizes = [
            "1-10", "11-50", "51-200", "201-500",
            "501-1000", "1001-5000", "5001-10000", "10001+"
        ]
        if number_of_employees not in valid_sizes:
            raise ValueError(f"Company size must be one of {', '.join(valid_sizes)}")
        
        return number_of_employees

    @field_validator('industry_type')
    def validate_industry_type(cls, industry_type):
        return validate_industry_type(industry_type=industry_type)

    @field_validator("about")
    def validate_about(cls, about):
        if about.strip() in {"", '""'}:
            return None
        ALLOWED_PATTERN = re.compile(r'^[a-zA-Z0-9.,?!:;\'"(){}\[\]<>_\-&@/\\+\s]+$')
        if not ALLOWED_PATTERN.match(about):
            raise ValueError("Text contains invalid characters.")
        validate_length(value=about, min_len=50, max_len=1000, field_name=COMPANY_ABOUT_FIELD)
        return about
       
    @field_validator('instagram')
    def validate_instagram(cls, instagram):
        if instagram.strip() in {"", '""'}:
            return None
        validate_instagram_url(value=instagram)
        validate_length(value=instagram, min_len=5, max_len=100, field_name=COMPANY_INSTAGRAM_FIELD)
        return instagram
    
    @field_validator('facebook')
    def validate_facebook(cls, facebook):
        if facebook.strip() in {"", '""'}:
            return None
        validate_facebook_url(value=facebook)
        validate_length(value=facebook, min_len=5, max_len=100, field_name=COMPANY_FACEBOOK_FIELD)
        return facebook
    
    @field_validator('twitter')
    def validate_twitter(cls, twitter):
        if twitter.strip() in {"", '""'}:
            return None
        validate_twitter_url(value=twitter)
        validate_length(value=twitter, min_len=5, max_len=100, field_name=COMPANY_TWITTER_FIELD)
        return twitter
        
    @field_validator('tagline')
    def validate_tagline(cls, tagline):
        if tagline.strip() in {"", '""'}:
            return None
        return tagline

class RemoveImageModel(BaseModel):
    path: str

class IndustryType(BaseModel):
    industry_type: str

    @field_validator('industry_type')
    def validate_industry_type(cls, industry_type):
        is_non_empty(value=industry_type, field_name="industry_type")
        return industry_type
    

class Department(BaseModel):
    department: str

    @field_validator('department')
    def validate_department(cls, department):
        is_non_empty(value=department, field_name="department")
        return department
    
    
class Designation(BaseModel):
    designation: str

    @field_validator('designation')
    def validate_department(cls, designation):
        is_non_empty(value=designation, field_name="designation")
        return designation
    
class CreateMetadata(BaseModel):
    name: str

    @field_validator('name')
    def validate_name(cls, name):  
        is_non_empty(value=name, field_name="name")
        return name
