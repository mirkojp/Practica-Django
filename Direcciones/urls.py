# from .views import (
#     DireccionViewSet,
#     obtener_info_ubicacion,
#     guardar_direccion,
#     obtener_direccion,
#     recalcular_y_guardar_direccion,
# )

# # Configurar el router para el ViewSet
# router = DefaultRouter()
# router.register(r"direcciones", DireccionViewSet, basename="direccion")


# urlpatterns = [
#     # Rutas existentes
#     path(
#         "obtener-info-ubicacion/", obtener_info_ubicacion, name="obtener_info_ubicacion"
#     ),
#     path("guardar-direccion/", guardar_direccion, name="guardar_direccion"),
#     path(
#         "obtener_direccion/<int:id_direccion>/",
#         obtener_direccion,
#         name="obtener_direccion",
#     ),
#     # Nueva ruta para recalcular y guardar
#     path(
#         "recalcular-y-guardar-direccion/",
#         recalcular_y_guardar_direccion,
#         name="recalcular_y_guardar_direccion",
#     ),
#     # # Rutas del ViewSet
#     # path("", include(router.urls)),
# ]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import crear_direccion, obtener_direccion, obtener_todas_direcciones, obtener_direcciones_sin_compra_antiguas,eliminar_direcciones_sin_compra_antiguas

urlpatterns = [
    path("crear-direccion", crear_direccion, name="crear-direccion"),
    path("direcciones/<int:id>", obtener_direccion, name="obtener-direccion"),
    path("direcciones/", obtener_todas_direcciones, name="obtener_todas_direcciones"),
    path(
        "direcciones/sin-compra-antiguas/",
        obtener_direcciones_sin_compra_antiguas,
        name="obtener_direcciones_sin_compra_antiguas",
    ),
    path(
        "direcciones/sin-compra-antiguas/eliminar/",
        eliminar_direcciones_sin_compra_antiguas,
        name="eliminar_direcciones_sin_compra_antiguas",
    ),
]
