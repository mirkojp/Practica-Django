from django.urls import path
from . import views

urlpatterns = [
    path("carritos", views.carritos, name="carritos"),
    path("compras", views.compras, name="compras"),
    path("compras/<int:id>", views.operaciones_compras, name="operaciones_compras"),
    # path("proceso-pago/", views.ProcesoPagoAPIView.as_view(), name="proceso_pago"),
    # path("create_preference/", views.CreatePreference, name="create_preference"),
    path(
        "create-preference-from-cart/",
        views.CreatePreferenceFromCart,
        name="create_preference_from_cart",
    ),
    path(
        "webhook/mercado-pago/", views.mercado_pago_webhook, name="mercado_pago_webhook"
    ),
]
