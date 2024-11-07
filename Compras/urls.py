from django.urls import path
from . import views

urlpatterns = [
    path("carritos", views.carritos, name="carritos"),
    path("compras", views.compras, name="compras"),
    path("compras/<int:id>", views.operaciones_compras, name="operaciones_compras"),
    path("proceso-pago/", views.ProcesoPagoAPIView.as_view(), name="proceso_pago"),
]
