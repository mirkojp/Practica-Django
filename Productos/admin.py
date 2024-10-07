from django.contrib import admin
from Productos.models import Funko,Categoría,Descuento,FunkoDescuento
# Register your models here.
admin.site.register(Funko)
admin.site.register(Categoría)
admin.site.register(Descuento)
admin.site.register(FunkoDescuento)
