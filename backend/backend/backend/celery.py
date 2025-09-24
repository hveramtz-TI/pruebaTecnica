import os
from celery import Celery

# Configurar el módulo de settings de Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# Usar una string aquí significa que el worker no necesita serializar
# la configuración cuando usa esta configuración
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configuración explícita para Redis - DESPUÉS de cargar settings de Django
app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Mexico_City',
)

# Cargar módulos de tareas desde todas las apps registradas
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')