from rest_framework import serializers
from .models import Usuario, Reseña

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["idUsuario", "nombre", "password", "contacto", "email"]

class ReseñaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reseña
        fields = ["idReseña", "contenido", "esetrellas", "fecha"]