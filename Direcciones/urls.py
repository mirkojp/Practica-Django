from django.urls import path
from .views import obtener_provincias, localidades_por_provincia, crear_direccion, listar_direccion, localidades_censales_por_provincia
from .views import calles_por_localidad_censal

urlpatterns = [
    path("obtener_provincias/", obtener_provincias, name="obtener_provincias"),
    path(
        "localidades/<str:id_provincia>/",
        localidades_por_provincia,
        name="localidades_por_provincia",
    ),
    path(
        "localidades-censales/<str:id_provincia>/",
        localidades_censales_por_provincia,
        name="localidades_censales_por_provincia",
    ),
    path("direcciones/", crear_direccion, name="crear_direccion"),
    path("direcciones/<int:id_direccion>/", listar_direccion, name="listar_direccion"),
    path(
        "calles/<str:id_provincia>/<str:id_localidad_censal>/",
        calles_por_localidad_censal,
        name="calles_por_localidad_censal",
    ),
]
