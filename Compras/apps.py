from django.apps import AppConfig


class ComprasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Compras'

class ComprasConfig(AppConfig):
    name = 'Compras'

    def ready(self):
        import Compras.signals