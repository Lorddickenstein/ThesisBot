from datetime import datetime
from dateutil import tz


def utc_to_local(utc) -> str:
    """ convert utc to local time """

    # CODE: found at https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime

    # auto-detect time zones
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    utc = utc.astimezone(to_zone).strftime('%Y-%m-%d %H:%M:%S')
    return utc


def get_local_time_now(format='%Y-%m-%d %H:%M:%S') -> datetime:
    """ return local time as string """

    now = datetime.now().strftime(format)
    now = datetime.strptime(now, format)
    return now


def get_uct_time(str) -> datetime:
    """ return utc time from string """
    return datetime.fromisoformat(str)


def get_datetime(str, format='%Y-%m-%d %H:%M:%S') -> datetime:
    """ returns datetime obj """
    return datetime.strptime(str, format)

def format_date(datetime_obj, format='%b %d, %Y %I:%M %p') -> str:
    """ returns formatted date """
    return datetime_obj.strftime(format)
