from django.urls import path
from gerenciamento import views
from django.urls import include

app_name = 'gerenciamento'

urlpatterns = [
    path('whoami/', views.whoami, name='whoami'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
] 
