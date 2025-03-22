from datetime import datetime


# Function to extract candidate's name from resume text
def get_candidate_name(file_name):
    candidate_name = file_name.split('.')[0]
    return candidate_name


def convert_nulls_to_empty_strings(data):
    if isinstance(data, dict):  # If the data is a dictionary
        return {key: convert_nulls_to_empty_strings(value) for key, value in data.items()}
    elif data is None or data == "Not Provided":  # If the value is None (null)
        return ""
    else:
        return data

def reformat_date(date_str):
    try:
        # Try to convert MM/DD/YYYY to ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)
        return datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError):
        try:
            # Try to convert DD-MM-YYYY to ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)
            return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError):
            return ""  


def deep_update(source: dict, overrides: dict) -> dict:
    """Performs a deep update of a dictionary, i.e. updates nested dictionaries.

    Args:
        source (dict): The dictionary to be updated.
        overrides (dict): The dictionary containing the overrides.

    Returns:
        dict: The updated dictionary.
    """
    
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(source.get(key), dict):
            source[key] = deep_update(source[key], value)
        else:
            source[key] = value
    return source


# Optimized flatten_dict_solr
def flatten_dict_solr(data: dict, parent_key: str = "", sep: str = ".") -> dict:
    """
    Flattens a nested dictionary for Solr indexing, converting nested keys into a single level with dot-separated keys.

    Args:
        data (dict): The dictionary to be flattened.
        parent_key (str, optional): The base key to prefix to each key in the result. Defaults to "".
        sep (str, optional): The separator to use between parent and child keys. Defaults to ".".

    Returns:
        dict: A flattened dictionary with keys suitable for Solr indexing. Keys "id", "file_upload", and "original_file" are ignored.
    """
    items = {}
    for k, v in data.items():
        if k in ["id", "file_upload", "original_file"]:
            continue  # Ignore specified keys

        # Direct key assignment for nested objects like 'social_media' or 'personal_information'
        new_key = k if parent_key in ["personal_information", "job_information", "social_media"] else (
            f"{parent_key}{sep}{k}" if parent_key else k
        )

        # Handle nested dictionaries
        if isinstance(v, dict) and parent_key in ["social_media", "personal_information", "job_information"]:
            items.update(flatten_dict_solr(v, "", sep=sep))  # Flatten without prefix for Solr
        elif isinstance(v, dict):
            items.update(flatten_dict_solr(v, new_key, sep=sep))
        elif isinstance(v, list):
            items[new_key] = {"set": v}
        else:
            items[new_key] = {"set": v}

    return items
