import os
from celery import Celery

# Configurar el módulo de settings de Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# Usar una string aquí significa que el worker no necesita serializar
# la configuración cuando usa esta configuración
app.config_from_object('django.conf:settings', namespace='CELERY')

# Cargar módulos de tareas desde todas las apps registradas
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')