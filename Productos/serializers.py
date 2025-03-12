from rest_framework import serializers
from .models import Funko, Descuento, FunkoDescuento, Categoría, Imagen


class ImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imagen
        fields = "__all__"  # Todos los campos de Imagen


class CategoríaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoría
        fields = "__all__"  # Todos los campos de Categoría


class FunkoSerializer(serializers.ModelSerializer):
    imagen = serializers.PrimaryKeyRelatedField(
        queryset=Imagen.objects.all(), allow_null=True, required=False
    )  # Usamos solo la ID de la imagen
    
    categoría = serializers.PrimaryKeyRelatedField(
        queryset=Categoría.objects.all(), many=True, required=False
    )  # Lista de IDs de categorías

    class Meta:
        model = Funko
        fields = [
            "idFunko",
            "nombre",
            "descripción",
            "is_backlight",
            "stock",
            "precio",
            "imagen",  # Ahora devuelve solo la ID de la imagen
            "categoría",  # Lista de IDs de categorías
        ]

class DescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descuento
        fields = ["idDescuento", "nombre", "porcentaje"]

class FunkoDescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunkoDescuento
        fields = ["idFunkoDescuento", "fecha_inicio", "fecha_expiracion", "funko", "descuento"]
