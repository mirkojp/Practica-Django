from rest_framework import serializers
from .models import Carrito, CarritoItem, Compra, CompraItem

class CarritoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarritoItem
        fields = ["idCarritoItem", "cantidad", "subtotal", "carrito", "funko"]

class CompraItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompraItem
        fields = ['idCompraItem', 'cantidad', 'subtotal', 'funko']
        depth = 1  # Esto te permitirá ver los detalles del funko

class CompraSerializer(serializers.ModelSerializer):
    items = CompraItemSerializer(many=True, read_only=True, source='items')

    class Meta:
        model = Compra
        fields = [
            'idCompra',
            'subtotal',
            'total',
            'fecha',
            'estado',
            'usuario',
            'direccion',
            'items',  # Incluye los items de compra relacionados
        ]
        depth = 1  # Puedes ajustar la profundidad si quieres ver más detalles de relaciones