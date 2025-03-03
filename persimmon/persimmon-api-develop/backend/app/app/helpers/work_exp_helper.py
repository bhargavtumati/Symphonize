from datetime import datetime
import json
import re

def parse_date_range(date_range: str):
    # Define possible date formats
    date_formats = [
        "%b’ %y",  # Example: "Feb’ 19"
        "%b’-%y",  # Example: "Feb’-19"
        "%b’ %Y",  # Example: "Feb’ 2019"
        "%b’-%Y",  # Example: "Feb’-2019"
        "%m/%Y",   # Example: "01/2025"
        "%m %Y",   # Example: "01 2025"
        "%m %y",   # Example: "01 25"
        "%b/%y",   # Example: "Jan/25"
        "%b %y",   # Example: "Jan 25"
        "%b/%Y",   # Example: "Jan/2025"
        "%b %Y",   # Example: "Jan 2025"
        "%m-%Y",   # Example: "01-2025"
        "%b-%y",   # Example: "Jan-25"
        "%b-%Y",   # Example: "Jan-2025"
        "%Y/%m",   # Example: "2025/01"
        "%Y-%m",   # Example: "2025-01"
        "%Y-%b",   # Example: "2025-jan"
        "%Y %b",   # Example: "2025 jan"
    ]

    # Split the range into start and end parts
    start_str, end_str = map(str.strip, date_range.split("-"))

    # Try different formats for both start and end dates
    def parse_date(date_str):
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {date_str}")

    try:
        start_date = parse_date(start_str)
        end_date = parse_date(end_str)
        # Calculate the difference
        diff_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month +1)
        experience_years = diff_months / 12
        return round(experience_years, 2)
    except Exception as e:
        print(f"Error calculating experience for '{date_range}': {e}")
        return 0.0


def process_resume_json(json_data):
    """
    Process resume JSON and calculate experience for each role and overall experience
    """
    try:
        # Parse JSON if it's a string
        if isinstance(json_data, str):
            resume_data = json.loads(json_data)
        else:
            resume_data = json_data
            
        # Get experience entries
        experience_entries = resume_data.get('experience', [])
        
        total_experience = 0.0
        processed_entries = []
        
        # Process each experience entry
        for entry in experience_entries:
            date_range = entry.get('dates')
            if date_range:
                experience_years = parse_date_range(date_range)
                entry['experience_years'] = experience_years
                total_experience += experience_years
                
                # Add processed entry with detailed calculation
                processed_entries.append({
                    'company': entry.get('company', ''),
                    'date_range': date_range,
                    'calculated_experience': experience_years
                })
        
        # Round total experience to 1 decimal place
        total_experience = round(total_experience, 1)
        
        return {
            'experience_details': processed_entries,
            'total_experience': total_experience,
            'processed_json': resume_data
        }
        
    except Exception as e:
        print(f"Error processing resume JSON: {e}")
        return None