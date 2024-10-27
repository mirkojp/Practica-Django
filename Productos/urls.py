from django.urls import path
from . import views

urlpatterns = [
    path('funkos', views.funkos, name="funkos"),
    path('funkos/<int:id>', views.operaciones_funkos, name="operaciones_funkos"),
    path('funkos/<int:id>/agregar_favoritos', views.agregar_favorito, name="agregar_favorito"),
    path('descuentos', views.descuentos, name="descuentos"),
    path('descuentos/<int:id>', views.operaciones_descuentos, name="operaciones_descuentos"),
    path('funkodescuentos', views.funkoDescuentos, name="funkoDescuentos"),
    path('funkodescuentos/<int:id>', views.op_funkoDescuentos, name="op_funkoDescuentos"),
]