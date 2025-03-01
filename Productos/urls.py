from django.urls import path
from . import views
from .views import ImagenView

urlpatterns = [
    path('funkos', views.funkos, name="funkos"),
    path('funkos/<int:id>', views.operaciones_funkos, name="operaciones_funkos"),
    path('funkos/<int:id>/favoritos', views.favoritos, name="favoritos"),
    path('descuentos', views.descuentos, name="descuentos"),
    path('descuentos/<int:id>', views.operaciones_descuentos, name="operaciones_descuentos"),
    path('funkodescuentos', views.funkoDescuentos, name="funkoDescuentos"),
    path('funkodescuentos/<int:id>', views.op_funkoDescuentos, name="op_funkoDescuentos"),
    path('categorias', views.categorias, name="categorias"),
    path('categorias/<int:id>', views.op_categorias, name="op_categorias"),
    path("imagen/", ImagenView.as_view(), name="crear_listar_imagenes"),
    path("imagen/<int:idImagen>/", ImagenView.as_view(), name="detalle_imagen"),
    
]
