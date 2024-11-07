from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from Usuarios.models import Token, Usuario
from .models import Carrito, CarritoItem, Compra, CompraItem
from datetime import date
from .serializers import CarritoItemSerializer, CompraItemSerializer, CompraSerializer
from Productos.models import Funko, FunkoDescuento, Descuento
from django.db import IntegrityError
from django.db import transaction
from Utils.tokenAuthorization import userAuthorization, adminAuthorization
from django.db.models import Q
from decorators.token_decorators import token_required, token_required_admin
from rest_framework.views import APIView
from django.conf import settings
import mercadopago
import json


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
        
    elif request.method == "DELETE":

        # Verificar que el ID del Funko fue proporcionado
        id_funko = request.data.get("idFunko")
        if not id_funko:
            return Response({"error": "Falta el ID del Funko a eliminar."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtener el carrito del usuario
            carrito = Carrito.objects.get(usuario=usuario)

            # Obtener el CarritoItem con el Funko especificado
            carrito_item = CarritoItem.objects.get(carrito=carrito, funko__idFunko=id_funko)

            # Actualizar el total en el carrito
            with transaction.atomic():
                carrito.total -= carrito_item.subtotal
                carrito_item.delete()
                carrito.save()

            return Response(
                {"Mensaje": "Funko eliminado del carrito correctamente."},
                status=status.HTTP_200_OK
            )

        except Carrito.DoesNotExist:
            return Response({"error": "Carrito no encontrado para el usuario."}, status=status.HTTP_404_NOT_FOUND)
        except CarritoItem.DoesNotExist:
            return Response({"error": "El Funko especificado no está en el carrito."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    elif request.method == "GET":
        try:
            # Obtener el carrito del usuario
            carrito = Carrito.objects.get(usuario=usuario)

            # Obtener todos los CarritoItem en el carrito
            carrito_items = CarritoItem.objects.filter(carrito=carrito)

            # Serializar los CarritoItem para obtener los datos del Funko y la cantidad
            serializer = CarritoItemSerializer(carrito_items, many=True)

            return Response(
                {
                    "Mensaje": "Lista de Funkos en el carrito.",
                    "CarritoItems": serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Carrito.DoesNotExist:
            return Response({"error": "Carrito no encontrado para el usuario."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST", "GET"])
@token_required
def compras(request, usuario):

    if request.method == "POST":
        # Obtener el ID de la dirección desde el body de la request
        id_direccion = request.data.get("idDireccion")
        if not id_direccion:
            return Response({"error": "Falta el ID de la dirección."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtener el carrito del usuario y verificar si contiene items
            carrito = Carrito.objects.get(usuario=usuario)
            carrito_items = CarritoItem.objects.filter(carrito=carrito)
            if not carrito_items.exists():
                return Response({"error": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

            # Crear la compra con valores temporales de subtotal y total
            today = date.today()
            compra = Compra.objects.create(
                usuario=usuario,
                direccion_id=id_direccion,
                subtotal=0,  # Valor temporal
                total=0,     # Valor temporal
                fecha=today,
                estado="PENDIENTE"
            )

            # Variables para calcular el subtotal y total de la compra
            subtotal_compra = 0

            # Crear las líneas de compra (CompraItem) a partir de los items del carrito
            with transaction.atomic():
                for item in carrito_items:
                    # Crear el CompraItem basado en cada CarritoItem
                    compra_item = CompraItem.objects.create(
                        compra=compra,
                        funko=item.funko,
                        cantidad=item.cantidad,
                        subtotal=item.subtotal
                    )
                    # Sumar el subtotal del item al subtotal total de la compra
                    subtotal_compra += compra_item.subtotal

                # Actualizar subtotal y total en la compra
                compra.subtotal = subtotal_compra
                compra.total = subtotal_compra  # Ajusta si necesitas aplicar impuestos o costos adicionales
                compra.save()

                # Limpiar el carrito después de crear la compra
                carrito.items.all().delete()  # Eliminar todos los CarritoItems
                carrito.total = 0  # Reiniciar el total del carrito
                carrito.save()

            # Serializar y devolver la compra creada
            serializer = CompraSerializer(compra)
            return Response(
                {
                    "Mensaje": "Compra creada exitosamente.",
                    "Compra": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        except Carrito.DoesNotExist:
            return Response({"error": "Carrito no encontrado para el usuario."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    elif request.method == "GET":
        try:
            # Si el usuario es admin, obten todas las compras; de lo contrario, solo las compras del usuario
            if usuario.is_staff:
                compras = Compra.objects.all()
            else:
                compras = Compra.objects.filter(usuario=usuario)

            # Serializar las compras
            serializer = CompraSerializer(compras, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PATCH", "GET"])
@token_required
def operaciones_compras(request, id, usuario):

    if request.method == "GET":
        try:
            # Buscar la compra con el id proporcionado
            compra = Compra.objects.get(idCompra=id)

            # Verificar si el usuario es admin o si la compra pertenece al usuario
            if usuario.is_staff or compra.usuario == usuario:
                # Serializar la compra
                serializer = CompraSerializer(compra)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # Si el usuario no es admin ni dueño de la compra, retornar un error
                return Response({"error": "No tienes permiso para acceder a esta compra."}, status=status.HTTP_403_FORBIDDEN)

        except Compra.DoesNotExist:
            return Response({"error": "Compra no encontrada."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == "PATCH":
        if not usuario.is_staff:
            # Solo los administradores pueden cambiar el estado de la compra
            return Response(
                {"error": "Permiso denegado. Solo los administradores pueden cambiar el estado de una compra."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            # Obtener la compra
            compra = Compra.objects.get(idCompra=id)

            # Validar que el nuevo estado esté en los cambios permitidos
            nuevo_estado = request.data.get("estado")

            if nuevo_estado not in ["ENVIADO", "ENTREGADO"]:
                return Response(
                    {"error": "El estado proporcionado no es válido. Solo se permite cambiar a 'ENVIADO' o 'ENTREGADO'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Cambios permitidos de estado
            if compra.estado == "PENDIENTE" and nuevo_estado == "ENVIADA":
                compra.estado = "ENVIADA"
            elif compra.estado == "ENVIADA" and nuevo_estado == "ENTREGADA":
                compra.estado = "ENTREGADA"
            else:
                return Response(
                    {"error": f"No se permite cambiar el estado de '{compra.estado}' a '{nuevo_estado}'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Guardar el cambio de estado
            compra.save()

            # Serializar y retornar la compra actualizada
            serializer = CompraSerializer(compra)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Compra.DoesNotExist:
            return Response({"error": "Compra no encontrada."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Codigo robado, esto no funciona todavia
#
class ProcesoPagoAPIView(APIView):
    def post(self, request):
        try:
            request_values = json.loads(request.body)
            payment_data = {
                "transaction_amount": float(request_values["transaction_amount"]),
                "token": request_values["token"],
                "installments": int(request_values["installments"]),
                "payment_method_id": request_values["payment_method_id"],
                "issuer_id": request_values["issuer_id"],
                "payer": {
                    "email": request_values["payer"]["email"],
                    "identification": {
                        "type": request_values["payer"]["identification"]["type"],
                        "number": request_values["payer"]["identification"]["number"]
                    }
                },

            }

            sdk = mercadopago.SDK(str(settings.MERCADOPAGO_ACCESS_TOKEN_TEST))

            payment_response = sdk.payment().create(payment_data)

            payment = payment_response["response"]
            status = {
                "id": payment["id"],
                "status": payment["status"],
                "status_detail": payment["status_detail"],
            }

            return Response(
                data={"body": status, "statusCode": payment_response["status"]},
                status=201,
            )
        except Exception as e:
            return Response(data={"body": payment_response}, status=400)
