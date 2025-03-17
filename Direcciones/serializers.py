

# class ProvinciaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Provincia
#         fields = ["idProvincia", "nombre"]


# class CiudadSerializer(serializers.ModelSerializer):
#     provincia = ProvinciaSerializer()  # Para anidar la relación con Provincia

#     class Meta:
#         model = Ciudad
#         fields = ["idCiudad", "nombre", "provincia"]


# class DirecciónSerializer(serializers.ModelSerializer):
#     ciudad = CiudadSerializer()  # Para anidar la relación con Ciudad

#     class Meta:
#         model = Dirección
#         fields = [
#             "idDireccion",
#             "calle",
#             "numero",
#             "contacto",
#             "email",
#             "codigo_postal",
#             "ciudad",
#         ]


from rest_framework import serializers
from .models import Coordenada, Provincia, Ciudad, Direccion


class CoordenadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordenada
        fields = "__all__"


class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincia
        fields = "__all__"


class CiudadSerializer(serializers.ModelSerializer):
    provincia = ProvinciaSerializer()

    class Meta:
        model = Ciudad
        fields = "__all__"


class DireccionSerializer(serializers.ModelSerializer):
    coordenada = CoordenadaSerializer()
    ciudad = CiudadSerializer()

    class Meta:
        model = Direccion
        fields = "__all__"
