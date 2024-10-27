from rest_framework import serializers
from .models import Funko, Descuento, FunkoDescuento

class FunkoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funko
        fields = ["idFunko", "nombre", "descripción", "is_backlight", "stock", "precio"]

class DescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descuento
        fields = ["idDescuento", "nombre", "porcentaje"]

class FunkoDescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunkoDescuento
        fields = ["idFunkoDescuento", "fecha_inicio", "fecha_expiracion", "funko", "descuento"]