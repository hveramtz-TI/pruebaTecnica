import re
from django.middleware.csrf import CsrfViewMiddleware
from django.conf import settings

class APICSRFExemptMiddleware(CsrfViewMiddleware):
    """
    Middleware personalizado que exime las rutas API de la verificación CSRF
    """
    
    def process_request(self, request):
        # Verificar si la ruta debe estar exenta de CSRF
        exempt_urls = getattr(settings, 'CSRF_EXEMPT_URLS', [])
        
        for url_pattern in exempt_urls:
            if re.match(url_pattern, request.path):
                # Marcar la vista como exempt
                setattr(request, '_dont_enforce_csrf_checks', True)
                break
                
        return super().process_request(request)
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Si la vista está marcada como exempt, no aplicar CSRF
        if getattr(request, '_dont_enforce_csrf_checks', False):
            return None
            
        return super().process_view(request, callback, callback_args, callback_kwargs)