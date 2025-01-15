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
