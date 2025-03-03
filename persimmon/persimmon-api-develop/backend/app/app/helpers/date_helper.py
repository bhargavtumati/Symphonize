from datetime import datetime, timezone
from sqlalchemy import  extract, Date, cast, text
from sqlalchemy.orm import Query
from fastapi import HTTPException

def date_filter_query_helper(query: Query, search_date: str, date_field, timezone: str = None):
    """Filters a SQLAlchemy query based on the provided `search_date` and the `date_field` field.
    
    The function supports filtering by:
    - Day: When the `search_date` is a single or two-digit number (e.g., "5" or "25"), it filters by day.
    - Year: When the `search_date` is a four-digit number (e.g., "2021"), it filters by year.
    - Month: When the `search_date` is a three-character month abbreviation (e.g., "Jan", "feb"), it filters by month.
    - Date: When the `search_date` is in a date format (e.g., "01-Jan-2021", "01/Jan/2021", "01-01-2021"), it filters by the full date.

    Args:
        query (sqlalchemy.orm.Query): The SQLAlchemy query object to apply the filter to.
        search_date (str): The date value to filter by, which can be in various formats (day, year, month, or full date).
        date_field : The datetime column to extract the date parts (day, month, year) from.
        timezone (str): The timezone to convert the UTC timestamp to before applying the filter.

    Returns:
        sqlalchemy.orm.Query: The updated query with the applied filter based on the search_date.
    """
    search_date = search_date.strip()
    if timezone:
        tz_conversion = text(f"{date_field} AT TIME ZONE 'UTC' AT TIME ZONE '{timezone}'")
    else:
        tz_conversion = date_field

    if len(search_date) == 2 or len(search_date) == 1:
        return query.filter(extract('day', tz_conversion).in_([int(search_date)]))
    if len(search_date) == 4:
        return query.filter(extract('year', tz_conversion).in_([int(search_date)]))
    if len(search_date) == 3:
        return query.filter(extract('month', tz_conversion).in_([datetime.strptime(search_date, "%b").month]))
    if len(search_date) == 5 or len(search_date) == 6:
        parsed_date = datetime.strptime(search_date, "%d %b")
        return query.filter(
            extract('month', tz_conversion) == parsed_date.month,
            extract('day', tz_conversion) == parsed_date.day
        )
    if 8 <= len(search_date) <= 11:
        date_formats = ["%d %b %Y", "%d %b %y", "%d %m %Y", "%d-%b-%Y", "%d/%b/%Y", "%d-%m-%Y", "%d/%m/%Y"]
        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(search_date, date_format).date()
                break
            except ValueError:
                continue  
        return query.filter(cast(tz_conversion, Date) == parsed_date)
    return query


def convert_epoch_to_utc(epoch_timestamp):
    """
    Converts an epoch Unix timestamp to a UTC datetime string in ISO 8601 format.

    Args:
        epoch_timestamp (int or float): The epoch Unix timestamp.

    Returns:
        str: The UTC datetime string in ISO 8601 format.
    """
    utc_time = datetime.fromtimestamp(epoch_timestamp, tz=timezone.utc)
    return utc_time.isoformat()

def calculate_duration_in_minutes(start_time, end_time):
    # Parse the strings into datetime objects
    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)
    if end <= start:
        raise HTTPException(status_code=400,detail="Start date/time cannot be greater than or equal to end date/time")
    # Calculate the difference in minutes
    duration = (end - start).total_seconds() / 60  # Convert seconds to minutes
    return int(duration)