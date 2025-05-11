from flask import current_app
from utils.time_utils import convert_to_vietnam_time

def formatdate(value, format='%d/%m/%Y %H:%M'):
    if isinstance(value, str):
        try:
            vietnam_time = convert_to_vietnam_time(value)
            return vietnam_time.strftime(format)
        except Exception as e:
            return value
    return value.strftime(format)