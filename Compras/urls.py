from django.urls import path
from . import views

urlpatterns = [
    path("carritos", views.carritos, name="carritos"),
    path("compras", views.compras, name="compras"),
    path("compras/<int:id>", views.operaciones_compras, name="operaciones_compras"),
    # path("proceso-pago/", views.ProcesoPagoAPIView.as_view(), name="proceso_pago"),
    path("create_preference/", views.CreatePreferenceView.as_view(), name="create_preference"),
    path("get_token/",views.getToken,name="get_token")
]
