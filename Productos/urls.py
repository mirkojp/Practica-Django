from django.urls import path
from . import views

urlpatterns = [
    path('funkos', views.funkos, name="funkos")
]