import datetime

def str_to_date(date_str: str) -> datetime.date | None:
    if not date_str:
        return None
    
    parts = date_str.split("-")
    year = int(parts[0])
    month = int(parts[1]) if len(parts) > 1 else 1
    day = int(parts[2]) if len(parts) > 2 else 1

    return datetime.date(year, month, day)