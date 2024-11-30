from pydantic import BaseModel, field_validator
import re
from app.utils.validators import is_non_empty, has_proper_characters, validate_length, validate_linkedin_company_url, validate_url, validate_industry_type
from app.models.company import CompanyTypeEnum

COMPANY_NAME_FIELD = "Company name"
COMPANY_WEBSITE_FIELD = "Website"
COMPANY_LINKEDIN_FIELD = "Company LinkedIn"

class CompanyModel(BaseModel):
    name: str
    website: str
    number_of_employees: str
    industry_type: str
    linkedin: str
    type: CompanyTypeEnum

    @field_validator('name')
    def validate_name(cls, name):
        is_non_empty(value=name, field_name=COMPANY_NAME_FIELD)
        has_proper_characters(value=name, field_name=COMPANY_NAME_FIELD)
        validate_length(value=name, min_len=3, max_len=50, field_name=COMPANY_NAME_FIELD)
        if not re.match(r'^[a-zA-Z0-9&\-\.\'\s]+$', name):
            raise ValueError("Company name can only contain alphanumeric characters, spaces, &, -, ., and '")
        return name

    @field_validator('website')
    def validate_website(cls, website):
        is_non_empty(value=website, field_name=COMPANY_WEBSITE_FIELD)
        validate_url(url=website)
        validate_length(value=website, min_len=5 , max_len=100, field_name=COMPANY_WEBSITE_FIELD)
        return website

    @field_validator('linkedin')
    def validate_linkedin(cls, linkedin):
        is_non_empty(value=linkedin, field_name=COMPANY_LINKEDIN_FIELD)
        validate_linkedin_company_url(value=linkedin)
        validate_url(url=linkedin)
        validate_length(value=linkedin, min_len=5, max_len=100, field_name=COMPANY_LINKEDIN_FIELD)
        if not re.match(r'^https://(www\.)?linkedin\.com/company/[a-zA-Z0-9\-_]{3,}(/.*)?/?$', linkedin):
            raise ValueError("The LinkedIn URL contains invalid characters")
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