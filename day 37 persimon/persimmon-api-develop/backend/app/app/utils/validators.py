import re
import validators
import tldextract
from app.models.master_data import MasterData


def is_non_empty(value: str, field_name: str) -> str:
    if not value.strip():
        raise ValueError(f"{field_name} is required")
    return value


def is_alphabetic(value: str, field_name: str) -> str:
    if not re.match(r"^[a-zA-Z\s]+$", value):
        raise ValueError(f"{field_name} should only contain alphabets")
    return value


def validate_letters_and_numbers(value: str, field_name: str) -> str:
    if not re.match(r"^[a-zA-Z0-9\s]+$", value):
        raise ValueError(f"Please enter letters or numbers only in {field_name}")
    return value


def has_proper_characters(value: str, field_name: str, char: str = " ") -> str:
    if value.startswith(char) or value.endswith(char) or f"{char}{char}" in value:
        if char == " ":
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
    if value[0] not in "6789":
        raise ValueError("Please enter a valid Whatsapp number")
    return value


def validate_linkedin_url(value: str) -> str:
    is_non_empty(value, "LinkedIn URL")
    pattern = (
        r"^(https://www.linkedin.com/in/|https://linkedin.com/in/)[A-Za-z0-9-_]+/?$"
    )
    if not re.match(pattern, value):
        raise ValueError("Please enter valid LinkedIn URL")
    return value


def validate_linkedin_company_url(value: str) -> str:
    if not (
        value.startswith("https://www.linkedin.com/company/")
        or value.startswith("https://linkedin.com/company/")
    ):
        raise ValueError("Please enter a valid LinkedIn Company URL")
    return value


def validate_professional_email(email: str) -> str:
    restricted_domains = [
        "gmail.com",
        "yahoo.com",
        "outlook.com",
        "aol.com",
        "mail.com",
        "icloud.com",
        "zoho.com",
        "yandex.com",
        "protonmail.com",
        "tutanota.com",
    ]
    domain = email.split("@")[-1]
    if domain in restricted_domains:
        raise ValueError("Please enter a valid professional email address")
    return email


def validate_url(url: str):
    if " " in url:
        raise ValueError("The URL cannot contain spaces")
    if not validators.url(url):
        raise ValueError("Please enter a valid URL")

    extracted = tldextract.extract(url)
    if extracted.domain == "www":
        raise ValueError("Please enter a valid URL")
    if extracted.subdomain == "www":
        if extracted.domain and extracted.suffix:
            return url
        else:
            raise ValueError("Please enter a valid URL")
    if extracted.domain and extracted.suffix:
        return url
    raise ValueError("Please enter a valid URL")


def validate_industry_type(industry_type: str):
    industry_type_exists = MasterData.validate_value_by_type(
        key="name", value=industry_type, type="Industry Type"
    )
    if not industry_type_exists:
        raise ValueError("Industry Type is not valid")
    return industry_type


def validate_job_location(location: str):
    location_exists = MasterData.validate_value_by_type(
        key="city", value=location, type="location"
    )
    if not location_exists:
        raise ValueError("Job location is not valid")
    return location


def validate_numeric_range(
    value: int, min_val: int, max_val: int, field_name: str
) -> int:
    if value < min_val:
        raise ValueError(f"Minimum value for {field_name} should be {min_val}")
    if value > max_val:
        raise ValueError(f"Maximum value for {field_name} should be {max_val}")
    return value
