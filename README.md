# 📟 Gestor de Inventario

**Gestor de Inventario** es una aplicación web desarrollada en **Django** para gestionar productos, categorías y usuarios en un sistema de inventario. Permite el registro de usuarios, la gestión de productos y categorías, el seguimiento del stock, así como operaciones CRUD completas con interfaz intuitiva basada en **Tailwind CSS**.

---

## 🚀 Características Principales

- 🔐 Autenticación de usuarios (registro, login y logout personalizados)
- 📦 Gestión de productos con precios, descripciones, categorías y stock
- 📂 CRUD de categorías
- 📉 Alerta de productos con bajo stock
- 📊 Dashboard con métricas clave
- 💅 Interfaz moderna usando Tailwind CSS
- ⚙️ Gestión de usuarios extendida con `PerfilUsuario` personalizado
- ⚠️ Decorador personalizado para requerir login (`@login_required`)
- 📁 Comando de consola para creación de categorías predeterminadas
- 🧪 Estructura de tests lista para pruebas unitarias

---

## 🏗️ Estructura del Proyecto

gestor-de-inventario/
├── gestor_inventario/ # Configuración global del proyecto Django
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
├── tasks/ # Aplicación principal
│ ├── models.py # Modelos de Usuario, Producto, Categoría
│ ├── views.py # Vistas con lógica de negocio
│ ├── forms.py # Formularios personalizados
│ ├── admin.py # Configuración del panel de administración
│ ├── templates/ # Plantillas HTML (Tailwind)
│ ├── decorators.py # Decoradores personalizados
│ └── management/commands/
│ └── crear_categorias.py # Script para poblar la BD con categorías
└── manage.py


---

## 🧑‍💻 Modelos

### `Categoria`
- `nombre`: CharField
- `descripcion`: TextField

### `Producto`
- `nombre`, `descripcion`, `precio`, `cantidad_stock`
- Relación con `Categoria`

### `PerfilUsuario` (Extiende `AbstractUser`)
- `telefono`, `direccion`
- Métodos sobrescritos para `set_password` y `check_password`

---

## 🔐 Autenticación

- Login y registro personalizados (no se usa el `AuthenticationForm` estándar)
- Decorador `@login_required` basado en sesiones manuales
- Vista `registro` implementada con `RegistroForm`

---

## 🖥️ Interfaces

### Dashboard
- Total de productos
- Total de categorías
- Productos con stock bajo (≤ 10 unidades)
- Modal para ingresar productos rápidamente

### Productos
- Listado general con filtro por categoría
- Acciones: Editar / Eliminar / Detalles

### Categorías
- Vista de todas las categorías con contador de productos

---

## ⚙️ Instalación y Uso

### Requisitos

- Python 3.10+
- PostgreSQL
- pip y entorno virtual (`venv`)

### Pasos

```bash
# Clonar el repositorio
git clone https://github.com/MateoRosero/Gestor-de-Inventario.git
cd Gestor-de-Inventario

# Crear entorno virtual
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar la base de datos (PostgreSQL)
# Verifica que los datos coincidan con settings.py

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser

# Crear categorías predeterminadas
python manage.py crear_categorias

# Ejecutar el servidor
python manage.py runserver

