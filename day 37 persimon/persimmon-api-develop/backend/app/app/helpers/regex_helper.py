import re


def get_domain_from_email(email: str) -> str:
    match = re.search(r"@([\w.-]+)", email)
    return match.group(1) if match else None
