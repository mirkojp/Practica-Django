from django.urls import path, re_path
from . import views

urlpatterns = [
    path('usuarios', views.register, name="usuarios"),
    path('usuarios/login', views.login, name="usuarios/login"),
    path('usuarios/<int:id>/', views.listar_usuario)
]