# Paws POS Pro - Backend API

Backend FastAPI para el sistema de punto de venta (POS) Paws POS Pro.

## 🚀 Características

- **Autenticación JWT**: Sistema seguro de autenticación con tokens
- **Gestión de Usuarios**: Roles (Admin, Manager, Cashier)
- **Gestión de Productos**: CRUD completo con categorías
- **Sistema de Ventas**: Registro de ventas con múltiples ítems
- **Control de Inventario**: Actualización automática de stock
- **Dashboard**: Estadísticas en tiempo real
- **Múltiples métodos de pago**: Efectivo, tarjeta, transferencia
- **Base de datos**: SQLAlchemy ORM (SQLite, PostgreSQL, MySQL)

## 📋 Requisitos

- Python 3.8+
- pip

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/AlejoG2903/paws-pos-pro.git
cd paws-pos-pro
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores
```

### 5. Ejecutar el servidor
```bash
# Desarrollo
uvicorn main:app --reload

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000
```

La API estará disponible en: `http://localhost:8000`

## 📚 Documentación de la API

Una vez que el servidor esté corriendo, puedes acceder a:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔐 Endpoints Principales

### Autenticación
- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/login` - Iniciar sesión
- `GET /auth/me` - Obtener información del usuario actual

### Categorías
- `GET /categories` - Listar categorías
- `POST /categories` - Crear categoría

### Productos
- `GET /products` - Listar productos (con filtros)
- `POST /products` - Crear producto
- `GET /products/{id}` - Obtener producto
- `PUT /products/{id}` - Actualizar producto
- `DELETE /products/{id}` - Desactivar producto

### Ventas
- `POST /sales` - Crear venta
- `GET /sales` - Listar ventas
- `GET /sales/{id}` - Obtener venta

### Dashboard
- `GET /dashboard/stats` - Estadísticas del día

## 🔑 Autenticación

La API usa JWT (JSON Web Tokens). Para acceder a endpoints protegidos:

1. Obtener token con `/auth/login`
2. Incluir el token en el header: `Authorization: Bearer {token}`

Ejemplo:
```bash
curl -X GET "http://localhost:8000/products" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 💾 Base de Datos

### SQLite (Desarrollo)
Por defecto usa SQLite, no requiere configuración adicional.

### PostgreSQL (Producción)
```bash
# Instalar driver
pip install psycopg2-binary

# Configurar en .env
DATABASE_URL=postgresql://usuario:password@localhost:5432/paws_pos_db
```

### MySQL
```bash
# Instalar driver
pip install pymysql

# Configurar en .env
DATABASE_URL=mysql+pymysql://usuario:password@localhost:3306/paws_pos_db
```

## 🧪 Datos de Prueba

Para crear un usuario admin inicial:

```python
# En Python:
from main import get_db, User, get_password_hash, UserRole
from sqlalchemy.orm import Session

db = next(get_db())

admin = User(
    email="admin@pawspos.com",
    username="admin",
    hashed_password=get_password_hash("admin123"),
    full_name="Administrador",
    role=UserRole.ADMIN
)

db.add(admin)
db.commit()
```

O usando la API:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@pawspos.com",
    "username": "admin",
    "password": "admin123",
    "full_name": "Administrador",
    "role": "admin"
  }'
```

## 📦 Estructura del Proyecto

```
backend/
├── main.py              # Aplicación principal
├── requirements.txt     # Dependencias
├── .env                 # Variables de entorno
├── .env.example         # Ejemplo de variables
└── paws_pos.db         # Base de datos SQLite (auto-generada)
```

## 🔒 Seguridad

- Las contraseñas se hashean con bcrypt
- Los tokens JWT expiran en 30 minutos (configurable)
- CORS configurado para permitir solo orígenes específicos
- Validación de datos con Pydantic

## 🚀 Despliegue en Producción

### Render / Railway / Fly.io
```bash
# Agregar Procfile:
web: uvicorn main:app --host 0.0.0.0 --port $PORT

# O usar gunicorn:
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT
```

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Integración con el Frontend

El frontend en React debe configurar la URL base de la API:

```typescript
// src/lib/api.ts
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  login: async (username: string, password: string) => {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    return response.json();
  },
  // ... más métodos
};
```

## 📝 Variables de Entorno Importantes

- `SECRET_KEY`: Clave secreta para JWT (¡cambiar en producción!)
- `DATABASE_URL`: URL de conexión a la base de datos
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Tiempo de expiración del token
- `CORS_ORIGINS`: Orígenes permitidos para CORS

## 🐛 Troubleshooting

### Error: "Secret key is not set"
Asegúrate de tener configurada la variable `SECRET_KEY` en `.env`

### Error: "Database connection failed"
Verifica que la `DATABASE_URL` sea correcta y el servidor de BD esté corriendo

### Error: "CORS policy blocked"
Agrega el origen de tu frontend a `CORS_ORIGINS` en `.env`

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

## 👨‍💻 Autor

Alejandro G - [@AlejoG2903](https://github.com/AlejoG2903)

## 🙏 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📧 Soporte

Para soporte o preguntas, abre un issue en GitHub.