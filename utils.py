from datetime import datetime
from config import TIMEZONE

def get_local_now():
    """Obtiene la fecha y hora actual en la zona horaria de Colombia"""
    return datetime.now(TIMEZONE)