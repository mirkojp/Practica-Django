from django.contrib import admin
from Direcciones.models import Provincia,Municipio,Departamento,Direccion,Coordenada
# Register your models here.
admin.site.register(Coordenada)
admin.site.register(Departamento)
admin.site.register(Municipio)
admin.site.register(Direccion)
admin.site.register(Provincia)
