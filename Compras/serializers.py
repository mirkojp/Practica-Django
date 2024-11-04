from rest_framework import serializers
from .models import Carrito, CarritoItem, Compra, CompraItem

class CarritoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarritoItem
        fields = ["idCarritoItem", "cantidad", "subtotal", "carrito", "funko"]