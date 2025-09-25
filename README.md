# 🌹 Sorteo San Valentín 2025 - Prueba Técnica# pruebaTecnica



Aplicación web completa para un sorteo de San Valentín donde los participantes pueden ganar una estadía romántica de 2 noches. La aplicación incluye registro de participantes, verificación por email, panel administrativo y sistema de notificaciones por correo electrónico.

## 🏗️ Arquitectura del Proyecto

### Backend (Django + Celery + Redis)
- **Django REST Framework** para API
- **Celery** para tareas asíncronas (envío de correos)
- **Redis** como broker de mensajería
- **JWT** para autenticación de administradores
- **SQLite** como base de datos (desarrollo)

### Frontend (Vue.js + TypeScript)
- **Vue 3** con Composition API
- **TypeScript** para tipado estático
- **Pinia** para manejo de estado
- **Vue Router** para navegación
- **Vite** como build tool

## 🚀 Configuración e Instalación

### Prerrequisitos
- Python 3.x
- Node.js 16+
- Redis Server (o Docker)
- Git

### 1. Backend Setup (Django)

```bash
# Navegar al directorio backend
cd backend/backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar archivo de configuración
copy .env.example .env

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

### 2. Redis Setup

**Opción A: Usando Docker (Recomendado)**
```bash
# Desde el directorio backend/backend
docker-compose up -d redis
```

**Opción B: Instalación local**
- Windows: Descargar desde [Redis Windows](https://github.com/microsoftarchive/redis/releases)
- macOS: `brew install redis`
- Ubuntu: `sudo apt install redis-server`

### 3. Frontend Setup (Vue.js)

```bash
# Navegar al directorio frontend
cd frontend/prueba

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev
```

## 🏃‍♂️ Ejecución del Sistema

### Paso 1: Iniciar Redis
```bash
# Si usas Docker
docker-compose up -d redis

# Si tienes Redis instalado localmente
redis-server
```

### Paso 2: Iniciar Celery Worker
```bash
# Desde backend/backend con el entorno virtual activado
celery -A backend worker --loglevel=info --pool=solo
```

### Paso 3: Iniciar Django Server
```bash
# Desde backend/backend con el entorno virtual activado
python manage.py runserver
```

### Paso 4: Iniciar Frontend
```bash
# Desde frontend/prueba
npm run dev
```

## 📁 Estructura del Proyecto

```
pruebaTecnica/
├── backend/backend/
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── settings.py          # Configuración Django
│   │   ├── celery.py           # Configuración Celery
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── emailer/
│   │   ├── models.py           # Modelos (Usuario, Concurso, Participante)
│   │   ├── views.py            # Endpoints REST API
│   │   ├── tasks.py            # Tareas asíncronas Celery
│   │   ├── serializers.py      # Serializers REST
│   │   ├── jwt_utils.py        # Utilidades JWT
│   │   └── middleware.py       # Middleware personalizado
│   ├── requirements.txt        # Dependencias Python
│   ├── docker-compose.yml      # Redis container
│   ├── .env.example           # Configuración ejemplo
│   └── manage.py
├── frontend/prueba/
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/
│   │   ├── router/
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 🔧 Configuración de Variables de Entorno

Editar el archivo `.env` en `backend/backend/`:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Redis y Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Settings (desarrollo)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@sorteo-san-valentin.com

# Email Settings (producción - descomentar para usar SMTP real)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=tu-email@gmail.com
# EMAIL_HOST_PASSWORD=tu-app-password

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-here
JWT_ACCESS_TOKEN_LIFETIME=20
JWT_REFRESH_TOKEN_LIFETIME=7
```

## 📧 Sistema de Correos Electrónicos

### Tareas Asíncronas Implementadas

1. **Email de Verificación** (`send_verification_email`)
   - Se envía cuando un usuario se registra
   - Contiene enlace para verificar email y crear contraseña
   - Diseño HTML responsivo con tema de San Valentín

2. **Email de Ganador** (`send_winner_notification_email`)
   - Se envía cuando un administrador selecciona un ganador
   - Notificación celebratoria con detalles del premio
   - Diseño HTML especial para la ocasión

### Configuración de Email

**Para Desarrollo (Console Backend):**
Los emails se muestran en la consola del servidor Django.

**Para Producción (SMTP):**
1. Configurar las variables de entorno de email en `.env`
2. Para Gmail, usar App Password (no contraseña regular)
3. Descomentar las líneas de configuración SMTP en `.env`

## 🎯 Endpoints de la API

### Endpoints Públicos

- `POST /api/register/` - Registro de participantes
- `POST /api/verify-email/` - Verificar email y crear contraseña
- `GET /api/verify-token/{token}/` - Validar token de verificación

### Endpoints de Administrador

- `POST /api/admin/create/` - Crear administrador
- `POST /api/admin/login/` - Login de administrador (JWT)
- `GET /api/admin/participants/` - Lista de participantes
- `POST /api/admin/select-winner/` - Seleccionar ganador
- `POST /api/admin/logout/` - Logout (invalidar token)

## 🧪 Pruebas y Desarrollo

### Probar Tareas de Celery desde Django Shell

```bash
# Acceder a Django shell
python manage.py shell

# Importar tareas
from emailer.tasks import send_verification_email, send_winner_notification_email

# Probar envío de verificación
send_verification_email.delay('usuario@test.com', 'token-test-123')

# Probar notificación de ganador
send_winner_notification_email.delay(user_id=1, contest_id=1)

# Ver estado de tareas
from celery import current_app
i = current_app.control.inspect()
i.active()
i.stats()
```

### Verificar Redis y Celery

```bash
# Verificar conexión Redis
redis-cli ping  # Debe responder: PONG

# Ver logs de Celery worker
# Los logs aparecen en la terminal donde ejecutaste el worker

# Ver tareas en Redis
redis-cli
> KEYS *
> LLEN celery  # Ver cola de tareas
```

### Comandos Útiles de Desarrollo

```bash
# Limpiar base de datos (datos de prueba)
POST /api/reset-database-for-testing/

# Ver participantes (requiere token admin)
GET /api/admin/participants/
Authorization: Bearer <your-jwt-token>

# Seleccionar ganador (requiere token admin)
POST /api/admin/select-winner/
Authorization: Bearer <your-jwt-token>
```

## 🔒 Seguridad

- **CSRF Protection**: Configurado para APIs
- **CORS**: Configurado para frontend local
- **JWT**: Tokens con expiración (20 min para admin)
- **Validación**: Serializers para todos los inputs
- **Sanitización**: Templates HTML seguros

## 🚀 Despliegue

### Para Producción:

1. Cambiar `DEBUG=False` en `.env`
2. Configurar base de datos PostgreSQL
3. Configurar servidor Redis dedicado
4. Configurar servidor de email SMTP
5. Configurar dominio en `ALLOWED_HOSTS`
6. Usar servidor web (nginx + gunicorn)
7. Configurar supervisor para Celery worker

## 🐛 Troubleshooting

### Problemas Comunes

**Error: Redis connection refused**
- Verificar que Redis esté ejecutándose: `redis-cli ping`
- Verificar puerto 6379 disponible
- Si usas Docker: `docker-compose up -d redis`

**Error: Celery tasks not executing**
- Verificar que el worker esté ejecutándose
- Verificar conexión a Redis
- En Windows usar: `--pool=solo`

**Error: Email not sending**
- En desarrollo: verificar logs en consola Django
- En producción: verificar configuración SMTP y credenciales

**Error: JWT token invalid**
- Verificar que JWT_SECRET_KEY sea consistente
- Verificar que el token no haya expirado (20 min)

## 📝 Licencia

Este proyecto es una prueba técnica y está disponible bajo licencia MIT.

---

**Desarrollado con ❤️ para San Valentín 2025** 🌹