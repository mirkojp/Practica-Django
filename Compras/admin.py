from django.contrib import admin
from Compras.models import Carrito,Compra,CarritoItem
# Register your models here.
admin.site.register(Carrito)
admin.site.register(Compra)
admin.site.register(CarritoItem)
