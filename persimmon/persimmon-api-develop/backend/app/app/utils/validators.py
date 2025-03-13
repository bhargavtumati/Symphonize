import json
import os
import re, io
from typing import List
from fastapi import HTTPException
from pytz import all_timezones
import validators
import tldextract
from app.models.master_data import MasterData
from PIL import Image

def is_non_empty(value: str, field_name: str) -> str:
    if not value.strip():
        raise ValueError(f"{field_name} is required")
    return value


def is_alphabetic(value: str, field_name: str) -> str:
    if not re.match(r'^[a-zA-Z\s]+$', value):
        raise ValueError(f"{field_name} should only contain alphabets")
    return value

def validate_letters_and_numbers(value: str, field_name: str) -> str:
    if not re.match(r'^[a-zA-Z0-9\s]+$', value):
        raise ValueError(f"Please enter letters or numbers only in {field_name}")
    return value

def has_proper_characters(value: str, field_name: str, char: str = ' ') -> str:
    if value.startswith(char) or value.endswith(char) or f'{char}{char}' in value:
        if char == ' ':
            raise ValueError(f"Please check for improper spaces in {field_name}")
    return value

def validate_length(value: str, min_len: int, max_len: int, field_name: str) -> str:
    value_without_spaces = value.replace(" ", "")
    if len(value_without_spaces) < min_len:
        raise ValueError(f"{field_name} should be at least {min_len} characters")
    if len(value) > max_len:
        raise ValueError(f"{field_name} cannot be more than {max_len} characters")
    return value


def validate_whatsapp_number(value: str) -> str:
    is_non_empty(value, "Whatsapp number")
    if not value.isdigit():
        raise ValueError("Whatsapp number can contain numeric values only")
    if len(value) != 10:
        raise ValueError("Please enter a valid 10 digit Whatsapp number")
    if value[0] not in '6789':
        raise ValueError("Please enter a valid Whatsapp number")
    return value


def validate_linkedin_url(value: str) -> str:
    is_non_empty(value, "LinkedIn URL")
    pattern = r'^(https://www.linkedin.com/in/|https://linkedin.com/in/)[A-Za-z0-9-_]+/?$'
    if not re.match(pattern, value):
        raise ValueError("Please enter valid LinkedIn URL")
    return value

def validate_linkedin_company_url(value: str) -> str:
    if not (value.startswith("https://www.linkedin.com/company/") or value.startswith("https://linkedin.com/company/")):
        raise ValueError("Please enter a valid LinkedIn Company URL")
    return value

def validate_instagram_url(value: str) -> str:
    is_non_empty(value, "Instagram URL")
    pattern = r'^(https://www.instagram.com/)[A-Za-z0-9-_.]{1,30}+/?$'
    if not re.match(pattern, value):
        raise ValueError("Please enter valid Instagram URL")
    return value

def validate_facebook_url(value: str) -> str:
    is_non_empty(value, "Facebook URL")
    pattern = r'^(https://www.facebook.com/)[A-Za-z0-9-_.]{5,50}+/?$'
    if not re.match(pattern, value):
        raise ValueError("Please enter valid Facebook URL")
    return value

def validate_x_url(value: str) -> str:
    is_non_empty(value, "X URL")
    pattern = r'^(https://x.com/)[A-Za-z0-9-_]{4,15}+/?$'
    if not re.match(pattern, value):
        raise ValueError("Please enter valid X URL")
    return value


def validate_professional_email(email: str) -> str:
    restricted_domains = [
        "gmail.com", "yahoo.com", "outlook.com", "aol.com",
        "mail.com", "icloud.com", "zoho.com", "yandex.com",
        "protonmail.com", "tutanota.com"
    ]
    domain = email.split('@')[-1]
    if domain in restricted_domains:
        raise ValueError("Please enter a valid professional email address")
    return email

def validate_url(url: str):
    if ' ' in url:
        raise ValueError("The URL cannot contain spaces")
    if not validators.url(url):
        raise ValueError("Please enter a valid URL")

    extracted = tldextract.extract(url)
    if extracted.domain == 'www':
        raise ValueError("Please enter a valid URL")
    if extracted.subdomain == 'www':
        if extracted.domain and extracted.suffix:
            return url
        else:
            raise ValueError("Please enter a valid URL")
    if extracted.domain and extracted.suffix:
        return url
    raise ValueError("Please enter a valid URL")

def validate_industry_type(industry_type: str):
    industry_type_exists = MasterData.validate_value_by_type(key="name", value=industry_type, type="Industry Type")
    if not industry_type_exists:
        raise ValueError("Industry Type is not valid")
    return industry_type

def validate_job_location(location: str):
    location_exists = MasterData.validate_value_by_type(key="city", value=location, type="location")
    if not location_exists:
        raise ValueError("Job location is not valid")
    return location

def validate_numeric_range(value: int, min_val: int, max_val: int, field_name: str) -> int:
    if value < min_val:
        raise ValueError(f"Minimum value for {field_name} should be {min_val}")
    if value > max_val:
        raise ValueError(f"Maximum value for {field_name} should be {max_val}")
    return value

def validate_decimal_point(value: float) -> float:  
    if round(value, 1) != value:
        raise ValueError('Enter only one digit after the decimal')
    return value

def validate_name_with_fullstop(value: str, field_name: str) -> str:
    if len(value) > 20:
        raise ValueError(f"{field_name} cannot be more than 20 characters")
    if value.startswith(" ") or value.endswith(" ") or "  " in value:
        raise ValueError(f"Please check for improper spaces")
    if not value.replace(" ", "").isalpha():
        raise ValueError(f"{field_name} should only contain alphabets")
    pattern = r"^[A-Za-z]+ [A-Za-z]+$"
    if not bool(re.match(pattern, value)):
        raise ValueError(f"Please enter your {field_name}, in 'First name Last name' format.")
    return value

def validate_mobile_number(number: int, field_name: str):
    pattern = r'^[6-9]\d{9}$' 
    if re.match(pattern, str(number)):
        return number
    else:
        raise ValueError(f"Please enter a valid {field_name}")

def validate_email_address(email_id:str, allowed_domains: list[str], field_name):
    email_id = email_id.lower()
    local, domain = email_id.split('@')

    if domain not in allowed_domains:
        raise ValueError(f"Please enter a valid {field_name}")
    
    pattern = r'^[a-zA-Z0-9.%+-]{3,}$' 

    if re.match(pattern, local):
        return email_id
    else:
        raise ValueError(f"Please enter a valid {field_name}")


#filter applicants
def validate_Preference(value: str):
    if value.lower() in {"good to have", "must have", "preferred to have"}:
        return value
    raise ValueError("The value for 'pref' must be one of the following: 'Good to have', 'Must have', or 'Preferred to have'.")

def get_education_institutions_list() ->list[str]:
    current_dir = os.path.dirname(__file__)
    college_names_list_json_file = os.path.join(current_dir, '..', 'datasets', 'college_names.json')
    with open(college_names_list_json_file, 'r') as file:
        data: List[str] = json.load(file)  
    return data

def validate_list_len(colors,length,field_name):
    if len(colors) > length:
        raise ValueError(f'Maximum {length} {field_name} are allowed in this list')
    return colors

def validate_timezone(tz: str) -> str:
    """Checks if the given timezone is valid."""
    if tz.title() not in all_timezones:
        raise HTTPException(status_code=400, detail=f"Invalid timezone: {tz}")
    return tz 

@staticmethod
def decode_and_validate_image(image):
        file_bytes = image.file.read()
        image.file.seek(0)  # Reset file pointer for future use

        # Validate if it's an image
        try:
            image = Image.open(io.BytesIO(file_bytes))
            if image.format not in ("JPEG", "PNG"):
                  raise ValueError("Only JPEG and PNG files are allowed.")
            image.verify()  # Verify the integrity of the image
        except Exception:
              raise ValueError("Invalid image file")