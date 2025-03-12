from django.urls import path
from . import views
from .views import ImagenListView

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
    path('imagenes/', ImagenListView.as_view(), name='imagenes-list'),
    path('imagenes/<int:imagen_id>/', ImagenListView.as_view(), name='imagen-detail'),
    path('categorias/<int:id>/gestionar', views.gestionar_funkos_categoria, name="gestionar_funkos_categoria"),
    path('funkos/<int:id>/reseñas', views.listar_reseñas_funko, name="listar_reseñas_funko"),
]
