from django.urls import path
from . import views

urlpatterns = [
    path('funkos', views.funkos, name="funkos"),
    path('funkos/<int:id>', views.operaciones_funkos, name="operaciones_funkos")
]