from django.urls import path
from . import views

urlpatterns = [
    # Contest routes (public)
    path('contest/register/', views.contest_register, name='contest_register'),
    path('verify-email/', views.verify_email_and_create_password, name='verify_email_create_password'),
    path('verify-token/<uuid:token>/', views.verify_token_validity, name='verify_token_validity'),
    path('reset-database/', views.reset_database_for_testing, name='reset_database_testing'),  # ⚠️ SOLO DESARROLLO
    
    # Admin authentication routes
    path('admin/create/', views.admin_create, name='admin_create'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('admin/verify-token/', views.admin_verify_token, name='admin_verify_token'),
    
    # Admin protected routes
    path('admin/participants/', views.admin_participants_list, name='admin_participants_list'),
]