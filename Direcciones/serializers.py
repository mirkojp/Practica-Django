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

    def create(self, validated_data):
        provincia_data = validated_data.pop("provincia")
        provincia, _ = Provincia.objects.get_or_create(**provincia_data)
        ciudad = Ciudad.objects.create(provincia=provincia, **validated_data)
        return ciudad

    def update(self, instance, validated_data):
        provincia_data = validated_data.pop("provincia", None)
        if provincia_data:
            provincia, _ = Provincia.objects.get_or_create(**provincia_data)
            instance.provincia = provincia
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class DireccionSerializer(serializers.ModelSerializer):
    coordenada = CoordenadaSerializer()
    ciudad = CiudadSerializer()

    class Meta:
        model = Direccion
        fields = "__all__"

    def create(self, validated_data):
        coordenada_data = validated_data.pop("coordenada")
        ciudad_data = validated_data.pop("ciudad")
        provincia_data = ciudad_data.pop("provincia")

        # Crear o obtener provincia
        provincia, _ = Provincia.objects.get_or_create(**provincia_data)
        # Crear o obtener ciudad
        ciudad, _ = Ciudad.objects.get_or_create(
            nombre=ciudad_data["nombre"], provincia=provincia
        )
        # Crear coordenada
        coordenada = Coordenada.objects.create(**coordenada_data)
        # Crear dirección
        direccion = Direccion.objects.create(
            coordenada=coordenada, ciudad=ciudad, **validated_data
        )
        return direccion

    def update(self, instance, validated_data):
        coordenada_data = validated_data.pop("coordenada", None)
        ciudad_data = validated_data.pop("ciudad", None)

        if coordenada_data:
            coordenada_serializer = CoordenadaSerializer(
                instance=instance.coordenada, data=coordenada_data, partial=True
            )
            if coordenada_serializer.is_valid():
                coordenada_serializer.save()

        if ciudad_data:
            provincia_data = ciudad_data.pop("provincia", None)
            if provincia_data:
                provincia, _ = Provincia.objects.get_or_create(**provincia_data)
                ciudad, _ = Ciudad.objects.get_or_create(
                    nombre=ciudad_data["nombre"], provincia=provincia
                )
                instance.ciudad = ciudad

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
