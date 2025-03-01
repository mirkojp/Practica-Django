from rest_framework import serializers
from .models import Funko, Descuento, FunkoDescuento, Categoría, Imagen


class FunkoSerializer(serializers.ModelSerializer):
    imagen = serializers.IntegerField(
        source="imagen.idImagen", allow_null=True, required=False
    )

    class Meta:
        model = Funko
        fields = [
            "idFunko",
            "nombre",
            "descripción",
            "is_backlight",
            "stock",
            "precio",
            "imagen",
        ]


class DescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descuento
        fields = ["idDescuento", "nombre", "porcentaje"]

class FunkoDescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunkoDescuento
        fields = ["idFunkoDescuento", "fecha_inicio", "fecha_expiracion", "funko", "descuento"]

class CategoríaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoría
        fields = ["idCategoria", "nombre"]

class ImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imagen
        fields = "__all__"
