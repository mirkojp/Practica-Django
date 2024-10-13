from django.urls import path, re_path
from . import views

urlpatterns = [
    #re_path('usuarios', views.register),
    re_path('usuarios/login', views.login),
]