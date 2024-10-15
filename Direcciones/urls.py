from django.urls import path
from .views import obtener_provincias, localidades_por_provincia, crear_direccion, listar_direccion

urlpatterns = [
    path("obtener_provincias/", obtener_provincias, name="obtener_provincias"),
    path(
        "localidades/<str:id_provincia>/",
        localidades_por_provincia,
        name="localidades_por_provincia",
    ),
    path("direcciones/", crear_direccion, name="crear_direccion"),
    path("direcciones/<int:id_direccion>/", listar_direccion, name="listar_direccion"),
]
