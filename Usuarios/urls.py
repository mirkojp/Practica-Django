from django.urls import path, re_path
from . import views

urlpatterns = [
    path('usuarios', views.register, name="usuarios"),
    path('usuarios/login', views.login, name="usuarios/login"),
    path('usuarios/<int:id>/', views.listar_usuario),
    path('usuarios/register_google/', views.register_google, name="register_google"),
    path('usuarios/login_google/', views.login_google, name="login_google"),
    path('usuarios/register_facebook/', views.register_facebook, name="register_facebook"),
    path('usuarios/login_facebook/', views.login_facebook, name="login_facebook"),
    path('auth/twitter/', views.twitter_login, name='twitter_login'),  # URL para iniciar el proceso de autenticación
    path('auth/twitter/callback/', views.twitter_callback, name='twitter_callback'),  # URL de callback para recibir los tokens
    path('auth/github/', views.github_login, name='github_login'),
    path('auth/github/callback/', views.github_callback, name='github_callback'),
]