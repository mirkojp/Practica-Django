from rest_framework import serializers
from .models import Provincia, Ciudad, Dirección


class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincia
        fields = ["idProvincia", "nombre"]


class CiudadSerializer(serializers.ModelSerializer):
    provincia = ProvinciaSerializer()  # Para anidar la relación con Provincia

    class Meta:
        model = Ciudad
        fields = ["idCiudad", "nombre", "provincia"]


class DirecciónSerializer(serializers.ModelSerializer):
    ciudad = CiudadSerializer()  # Para anidar la relación con Ciudad

    class Meta:
        model = Dirección
        fields = [
            "idDireccion",
            "calle",
            "numero",
            "contacto",
            "email",
            "codigo_postal",
            "ciudad",
        ]
