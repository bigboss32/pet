import os
from zoneinfo import ZoneInfo

# ✅ Configuración de zona horaria de Colombia
TIMEZONE = ZoneInfo("America/Bogota")

# Configuración de la aplicación
SECRET_KEY = os.getenv("SECRET_KEY", "tu-clave-secreta-muy-segura-cambiala-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./paws_pos.db")