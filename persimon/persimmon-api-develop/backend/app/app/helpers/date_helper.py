from datetime import datetime, timezone
from sqlalchemy import  extract, Date, cast
from sqlalchemy.orm import Query

def date_filter_query_helper(query: Query, search_date: str, date_field):
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

    Returns:
        sqlalchemy.orm.Query: The updated query with the applied filter based on the search_date.
    """
    search_date = search_date.strip()
     # Filter by day (if the search_date is 1 or 2 digits)
    if len(search_date) == 2 or len(search_date) ==1 :
        query = query.filter(
                extract('day', date_field).in_([int(search_date)])
            )
     # Filter by year (if the search_date is 4 digits)
    elif len(search_date) ==4 :
        query = query.filter(
                extract('year', date_field).in_([int(search_date)])
            )
     # Filter by month (if the search_date is a 3-letter month abbreviation)
    elif len(search_date) == 3:
        query = query.filter(
                extract('month', date_field).in_([datetime.strptime(search_date, "%b").month])
            )
    # Filter by full date (if the search_date is in a valid date format)
    elif len(search_date) >=9 or len(search_date) <= 11:
        date_formats = ["%d-%b-%Y", "%d/%b/%Y", "%d-%m-%Y", "%d/%m/%Y"]
        for date_format in date_formats:
            try:
                search_date =  datetime.strptime(search_date, date_format).date()
                break
            except ValueError:
                continue  
        query = query.filter(cast(date_field, Date) == search_date)  # Cast datetime to DATE

    return query

from datetime import datetime, timezone

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

