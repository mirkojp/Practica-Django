from rest_framework import serializers
from .models import Departamento,Municipio,Coordenada,Provincia,Direccion

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
from .models import Coordenada, Departamento, Municipio, Direccion, Provincia


class CoordenadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordenada
        fields = "__all__"


class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincia
        fields = "__all__"


class DepartamentoSerializer(serializers.ModelSerializer):
    provincia = ProvinciaSerializer()

    class Meta:
        model = Departamento
        fields = "__all__"


class MunicipioSerializer(serializers.ModelSerializer):
    departamento = DepartamentoSerializer()

    class Meta:
        model = Municipio
        fields = "__all__"


class DireccionSerializer(serializers.ModelSerializer):
    coordenada = CoordenadaSerializer()
    municipio = MunicipioSerializer()

    class Meta:
        model = Direccion
        fields = "__all__"
