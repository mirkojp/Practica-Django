from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from Usuarios.models import Token, Usuario
from .models import Carrito, CarritoItem
from datetime import date
from .serializers import CarritoItemSerializer
from Productos.models import Funko, FunkoDescuento, Descuento
from django.db import IntegrityError
from django.db import transaction
from Utils.tokenAuthorization import userAuthorization, adminAuthorization
from django.db.models import Q
from decorators.token_decorators import token_required, token_required_admin


# Create your views here.
@api_view(["POST", "GET", "DELETE"])
@token_required
def carritos(request, usuario):

    if request.method == "POST":

        # Verificar que el Funko y la cantidad fueron proporcionados
        id_funko = request.data.get("idFunko")
        cantidad = request.data.get("cantidad")
        if not id_funko or not cantidad:
            return Response({"error": "Falta el ID del Funko o la cantidad."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:

            # Obtener el carrito del usuario
            carrito = Carrito.objects.get(usuario=usuario)

            # Obtener el Funko
            funko = Funko.objects.get(idFunko=id_funko)

            # Obtener el precio del Funko considerando un posible descuento
            precio_funko = funko.precio
            today = date.today()
            
            descuento_activo = FunkoDescuento.objects.filter(
                funko=funko,
                fecha_inicio__lte=today,
                fecha_expiracion__gte=today
            ).first()
            
            if descuento_activo:
                descuento = Descuento.objects.get(idDescuento=descuento_activo.descuento.idDescuento)
                precio_funko *= (1 - (descuento.porcentaje / 100))

            # Calcular el subtotal de CarritoItem
            subtotal = precio_funko * cantidad

            # Crear el CarritoItem
            with transaction.atomic():
                carrito_item = CarritoItem.objects.create(
                    carrito=carrito,
                    funko=funko,
                    cantidad=cantidad,
                    subtotal=subtotal
                )

                # Actualizar el subtotal en Carrito
                carrito.total += subtotal
                carrito.save()
                

            # Serializar el CarritoItem creado
            serializer = CarritoItemSerializer(carrito_item)

            return Response(
                {
                    "Mensaje": "Funko agregado al carrito correctamente.",
                    "CarritoItem": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        except Carrito.DoesNotExist:
            return Response({"error": "Carrito no encontrado para el usuario."}, status=status.HTTP_404_NOT_FOUND)
        except Funko.DoesNotExist:
            return Response({"error": "Funko no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)