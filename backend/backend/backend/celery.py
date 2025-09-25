import os
from celery import Celery
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar el módulo de settings de Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# Usar una string aquí significa que el worker no necesita serializar
# la configuración cuando usa esta configuración
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configuración explícita para Redis usando variables de entorno
app.conf.update(
    broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Mexico_City',
    task_always_eager=False,  # Para que las tareas se ejecuten de forma asíncrona
    task_eager_propagates=True,
)

# Cargar módulos de tareas desde todas las apps registradas
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')