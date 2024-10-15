from rest_framework import serializers
from .models import Funko

class FunkoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funko
        fields = ["idFunko", "nombre", "descripción", "is_backlight", "stock", "precio"]