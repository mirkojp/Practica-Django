from django.urls import path
from . import views

urlpatterns = [
    path('carritos', views.carritos, name="carritos"),
    path('compras', views.compras, name="compras"),
]