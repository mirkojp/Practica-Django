from rest_framework import serializers

from Productos.models import Funko

class FunkoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funko
        fields = '__all__'