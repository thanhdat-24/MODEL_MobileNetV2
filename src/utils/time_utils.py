from datetime import datetime
import pytz

def convert_to_vietnam_time(utc_time):
    utc_tz = pytz.timezone('UTC')
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    
    if isinstance(utc_time, str):
        try:
            dt = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            try:
                dt = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                dt = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S')
    else:
        dt = utc_time
    
    dt_utc = utc_tz.localize(dt)
    dt_vietnam = dt_utc.astimezone(vietnam_tz)
    
    return dt_vietnam
