from django.urls import path
from . import views

urlpatterns = [
    # Contest routes (public)
    path('contest/register/', views.contest_register, name='contest_register'),
    path('verify-email/', views.verify_email_and_create_password, name='verify_email_create_password'),
    path('verify-token/<uuid:token>/', views.verify_token_validity, name='verify_token_validity'),
    path('reset-database/', views.reset_database_for_testing, name='reset_database_testing'),  # ⚠️ SOLO DESARROLLO
    
    # Admin authentication routes
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/refresh-token/', views.admin_refresh_token, name='admin_refresh_token'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('admin/profile/', views.admin_profile, name='admin_profile'),  # Ruta protegida
]