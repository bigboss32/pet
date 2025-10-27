# create_initial_data.py
# Ejecuta este script para crear datos iniciales en tu base de datos

import requests
import json

API_BASE = "http://localhost:8000"

def create_user(email, username, password, full_name, role="admin"):
    """Crear un usuario"""
    url = f"{API_BASE}/auth/register"
    data = {
        "email": email,
        "username": username,
        "password": password,
        "full_name": full_name,
        "role": role
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 201:
            print(f"✅ Usuario '{username}' creado exitosamente")
            return response.json()
        else:
            print(f"❌ Error al crear usuario '{username}': {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def login(username, password):
    """Iniciar sesión y obtener token"""
    url = f"{API_BASE}/auth/login"
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✅ Login exitoso para '{username}'")
            return token
        else:
            print(f"❌ Error en login: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def create_category(token, name, description=None):
    """Crear una categoría"""
    url = f"{API_BASE}/categories"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": name,
        "description": description
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            print(f"✅ Categoría '{name}' creada exitosamente")
            return response.json()
        else:
            print(f"❌ Error al crear categoría '{name}': {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def create_product(token, product_data):
    """Crear un producto"""
    url = f"{API_BASE}/products"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, json=product_data, headers=headers)
        if response.status_code == 201:
            print(f"✅ Producto '{product_data['name']}' creado exitosamente")
            return response.json()
        else:
            print(f"❌ Error al crear producto: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def main():
    print("=" * 60)
    print("CONFIGURACIÓN INICIAL DE PAWSPOS PRO")
    print("=" * 60)
    print()
    
    # 1. Crear usuarios
    print("📝 Creando usuarios...")
    print()
    
    admin = create_user(
        email="admin@petshop.com",
        username="admin",
        password="admin123",
        full_name="Administrador",
        role="admin"
    )
    
    cashier = create_user(
        email="cajero@petshop.com",
        username="cajero",
        password="cajero123",
        full_name="Cajero Principal",
        role="cashier"
    )
    
    print()
    
    if not admin:
        print("❌ No se pudo crear el usuario admin. Verifica que el backend esté corriendo.")
        return
    
    # 2. Login para obtener token
    print("🔑 Iniciando sesión con admin...")
    print()
    token = login("admin", "admin123")
    
    if not token:
        print("❌ No se pudo iniciar sesión")
        return
    
    # 3. Crear categorías
    print()
    print("📂 Creando categorías...")
    print()
    
    categories = [
        {"name": "Alimento", "description": "Alimentos para mascotas"},
        {"name": "Accesorio", "description": "Accesorios y complementos"},
        {"name": "Juguetes", "description": "Juguetes para mascotas"},
        {"name": "Medicamentos", "description": "Medicamentos y suplementos"},
        {"name": "Higiene", "description": "Productos de higiene y cuidado"},
    ]
    
    created_categories = {}
    for cat in categories:
        result = create_category(token, cat["name"], cat["description"])
        if result:
            created_categories[cat["name"]] = result["id"]
    
    # 4. Crear algunos productos de ejemplo
    print()
    print("📦 Creando productos de ejemplo...")
    print()
    
    if "Alimento" in created_categories:
        products = [
            {
                "name": "Alimento Premium Perro Adulto 15kg",
                "description": "Alimento balanceado premium para perros adultos",
                "price": 45000,
                "cost": 30000,
                "stock": 25,
                "category_id": created_categories["Alimento"],
                "barcode": "7891234567890"
            },
            {
                "name": "Alimento para Gato Adulto 10kg",
                "description": "Alimento completo para gatos adultos",
                "price": 38000,
                "cost": 25000,
                "stock": 30,
                "category_id": created_categories["Alimento"],
                "barcode": "7891234567891"
            },
        ]
        
        if "Accesorio" in created_categories:
            products.extend([
                {
                    "name": "Correa Retráctil 5m",
                    "description": "Correa retráctil para perros hasta 20kg",
                    "price": 25000,
                    "cost": 15000,
                    "stock": 15,
                    "category_id": created_categories["Accesorio"],
                    "barcode": "7891234567892"
                },
                {
                    "name": "Plato Doble Acero Inoxidable",
                    "description": "Plato doble para comida y agua",
                    "price": 18000,
                    "cost": 10000,
                    "stock": 20,
                    "category_id": created_categories["Accesorio"],
                }
            ])
        
        if "Juguetes" in created_categories:
            products.append({
                "name": "Pelota de Goma Maciza",
                "description": "Pelota resistente para perros",
                "price": 8000,
                "cost": 4000,
                "stock": 50,
                "category_id": created_categories["Juguetes"],
            })
        
        for product in products:
            create_product(token, product)
    
    print()
    print("=" * 60)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("Credenciales de acceso:")
    print()
    print("👤 Administrador:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print()
    print("👤 Cajero:")
    print("   Usuario: cajero")
    print("   Contraseña: cajero123")
    print()
    print("🌐 Accede a: http://localhost:5173")
    print("=" * 60)

if __name__ == "__main__":
    main()