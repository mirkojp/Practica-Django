from django.urls import path
from .views import obtener_provincias, localidades_por_provincia, localidades_censales_por_provincia
from .views import calles_por_localidad_censal, crear_direccion

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
    path(
        "calles/<str:id_provincia>/<str:id_localidad_censal>/",
        calles_por_localidad_censal,
        name="calles_por_localidad_censal",
    ),
    path("crear-direccion/", crear_direccion, name="crear_direccion"),
]
