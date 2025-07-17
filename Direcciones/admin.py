from django.contrib import admin
from Direcciones.models import Provincia, Ciudad, Direccion#, Coordenada

# Register your models here.
# admin.site.register(Coordenada)
admin.site.register(Ciudad)
admin.site.register(Direccion)
admin.site.register(Provincia)
