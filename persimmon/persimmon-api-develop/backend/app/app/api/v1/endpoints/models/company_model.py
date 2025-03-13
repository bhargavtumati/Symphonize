from fastapi import UploadFile
from pydantic import BaseModel, field_validator
import re, base64, imghdr
from app.utils.validators import is_non_empty, has_proper_characters, validate_length, validate_linkedin_company_url, validate_url, validate_industry_type, validate_instagram_url, validate_facebook_url, validate_x_url, decode_and_validate_image
from app.models.company import CompanyTypeEnum,BusinessTypeEnum
from typing import List, Optional

COMPANY_NAME_FIELD = "Company name"
COMPANY_WEBSITE_FIELD = "Website"
COMPANY_LINKEDIN_FIELD = "Company LinkedIn"
COMPANY_INSTAGRAM_FIELD = "Company Instagram"
COMPANY_FACEBOOK_FIELD = "Company Facebook"
COMPANY_X_FIELD = "Company X"

class CompanyModel(BaseModel):
    name: str
    website: str
    number_of_employees: str
    industry_type: str
    company_type: CompanyTypeEnum
    linkedin_url: str
    business_type: Optional[BusinessTypeEnum] = None
    about: Optional[str] = None
    tagline: Optional[str] = None
    facebook_url: Optional[str] = None
    x_url: Optional[str] = None
    instagram_url: Optional[str] = None
    logo: Optional[UploadFile] = None
    company_images: Optional[List[UploadFile]] = None    

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
        """
        Validates a company website URL based on the given rules.
        Rules:
        1. Must start with 'https://www.' or 'www.'
        2. Company name must be at least 3 characters.
        3. Domain must be one of: .in, .com, .net, .org
        4. Total length must be between 10 and 100 characters.
        
        Returns:
            True if valid, False otherwise.
        """
        pattern = r"^(https://www\.|www\.)[a-zA-Z0-9-]{3,}\.(in|com|net|org)$"
        if not (10 <= len(website) <= 100):
            return False  # Length validation
        #return bool(re.match(pattern, website))
        return website

    @field_validator('linkedin_url')
    def validate_linkedin(cls, linkedin_url):
        is_non_empty(value=linkedin_url, field_name=COMPANY_LINKEDIN_FIELD)
        validate_linkedin_company_url(value=linkedin_url)
        validate_url(url=linkedin_url)
        #Is the validate_length function is required
        validate_length(value=linkedin_url, min_len=5, max_len=100, field_name=COMPANY_LINKEDIN_FIELD)
        return linkedin_url

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
    
    @field_validator('company_type')
    def validate_company_type(company_type: CompanyTypeEnum) -> CompanyTypeEnum:
        if company_type not in CompanyTypeEnum:
            raise ValueError(f"Invalid company type. Allowed values: {[e.value for e in CompanyTypeEnum]}")
        return company_type
    
    @field_validator('business_type')
    def validate_business_type(business_type: BusinessTypeEnum) -> BusinessTypeEnum:
        if business_type not in BusinessTypeEnum:
            raise ValueError(f"Invalid business type. Allowed values: {[e.value for e in BusinessTypeEnum]}")
        return business_type

    @field_validator("about")
    def validate_about(cls, about):
        if about is None:  # ✅ Skip validation if None
            return about
        ALLOWED_PATTERN = re.compile(r'^[a-zA-Z0-9.,?!:;\'"(){}\[\]<>_\-&@/\\+\s]+$')
        if not ALLOWED_PATTERN.match(about):
            raise ValueError("Text contains invalid characters.")
        return about
    

    
    @field_validator('instagram_url')
    def validate_instagram(cls, instagram_url):
        if instagram_url is None:  # ✅ Skip validation if None
            return instagram_url
        validate_instagram_url(value=instagram_url)
        validate_url(url=instagram_url)
        #Is the validate_length function is required
        validate_length(value=instagram_url, min_len=5, max_len=100, field_name=COMPANY_INSTAGRAM_FIELD)
        return instagram_url
    
    @field_validator('facebook_url')
    def validate_facebook(cls, facebook_url):
        if facebook_url is None:  # ✅ Skip validation if None
            return facebook_url
        validate_facebook_url(value=facebook_url)
        validate_url(url=facebook_url)
        #Is the validate_length function is required
        validate_length(value=facebook_url, min_len=5, max_len=100, field_name=COMPANY_FACEBOOK_FIELD)
        return facebook_url
    
    @field_validator('x_url')
    def validate_x(cls, x_url):
        if x_url is None:  # ✅ Skip validation if None
            return x_url
        validate_x_url(value=x_url)
        validate_url(url=x_url)
        #Is the validate_length function is required
        validate_length(value=x_url, min_len=5, max_len=100, field_name=COMPANY_X_FIELD)
        return x_url
    
    @field_validator("logo")
    def validate_logo(cls, logo):
        if not logo:
            return logo
        decode_and_validate_image(logo)
        file_size = logo.file.seek(0, 2)  # Get file size in bytes
        logo.file.seek(0)  # Reset file pointer
        if file_size > 5 * 1024 * 1024:
            raise ValueError("Logo size must be less than 5MB.")
        return logo
    
    @field_validator("company_images")
    def validate_company_images(cls, company_images):
        if not company_images:
            return company_images
        if len(company_images)>10:
            raise ValueError("No of Company Images not to be more than 10")
        for image in company_images:
            decode_and_validate_image(image)
            file_size = image.file.seek(0, 2)  # Get file size in bytes
            image.file.seek(0)  # Reset file pointer
            if file_size > 5 * 1024 * 1024:
               raise ValueError("images size must be less than 5MB.")
        return company_images
    
