import uuid
from django.shortcuts import render
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
import urllib
from Usuarios.models import Token, Usuario
from .models import Carrito, CarritoItem, Compra, CompraItem
from datetime import date
from .serializers import CarritoItemSerializer, CompraItemSerializer, CompraSerializer
from Productos.models import Funko, FunkoDescuento, Descuento

from django.db import transaction
from django.db.models import Q
from decorators.token_decorators import (
    token_required,
    token_required_admin,
    token_required_without_user,
)
from rest_framework.views import APIView
from django.conf import settings
import mercadopago
import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from django.http import JsonResponse
from .services import validate_signature
import os
from django.http import HttpResponse
import logging
from .utils import send_email
from Direcciones.models import Direccion

logger = logging.getLogger(__name__)
# Create your views here.
@api_view(["POST", "GET", "DELETE"])
@token_required
def carritos(request, usuario):
    
    if request.method == "POST":
        # Verificar que el Funko y la cantidad fueron proporcionados
        id_funko = request.data.get("idFunko")
        cantidad = request.data.get("cantidad")
        if not id_funko or not cantidad:
            return Response(
                {"error": "Falta el ID del Funko o la cantidad."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Obtener el carrito del usuario
            carrito = Carrito.objects.get(usuario=usuario)

            # Obtener el Funko
            funko = Funko.objects.get(idFunko=id_funko)

            

            # Obtener el precio del Funko considerando un posible descuento
            precio_funko = funko.precio
            today = date.today()

            descuento_activo = FunkoDescuento.objects.filter(
                funko=funko, fecha_inicio__lte=today, fecha_expiracion__gte=today
            ).first()

            if descuento_activo:
                descuento = Descuento.objects.get(
                    idDescuento=descuento_activo.descuento.idDescuento
                )
                precio_funko *= 1 - (descuento.porcentaje / 100)

            # Verificar si ya existe un CarritoItem para este Funko
            with transaction.atomic():
                carrito_item = CarritoItem.objects.filter(
                    carrito=carrito, funko=funko
                ).first()


                if carrito_item:

                    # Verificar si la cantidad total excede el stock
                    cantidad_total = carrito_item.cantidad + cantidad
                    if cantidad_total > funko.stock:
                        return Response(
                            {
                                "error": f"No hay suficiente stock. Disponible."
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Actualizar cantidad y subtotal del CarritoItem existente
                    carrito_item.cantidad += cantidad
                    carrito_item.subtotal = precio_funko * carrito_item.cantidad
                    carrito_item.save()
                else:

                    # Verificar si la cantidad  excede el stock
                    if cantidad > funko.stock:
                        return Response(
                            {
                                "error": f"No hay suficiente stock. Disponible."
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Crear nuevo CarritoItem si no existe
                    subtotal = precio_funko * cantidad
                    carrito_item = CarritoItem.objects.create(
                        carrito=carrito, funko=funko, cantidad=cantidad, subtotal=subtotal
                    )

                # Actualizar el total del carrito
                carrito.total = sum(item.subtotal for item in CarritoItem.objects.filter(carrito=carrito))
                carrito.save()

            # Serializar el CarritoItem
            serializer = CarritoItemSerializer(carrito_item)

            return Response(
                {
                    "Mensaje": "Funko agregado al carrito correctamente.",
                    "CarritoItem": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except Carrito.DoesNotExist:
            return Response(
                {"error": "Carrito no encontrado para el usuario."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Funko.DoesNotExist:
            return Response(
                {"error": "Funko no encontrado."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    elif request.method == "DELETE":

        # Verificar que el ID del Funko fue proporcionado
        id_funko = request.data.get("idFunko")
        if not id_funko:
            return Response(
                {"error": "Falta el ID del Funko a eliminar."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Obtener el carrito del usuario
            carrito = Carrito.objects.get(usuario=usuario)

            # Obtener el CarritoItem con el Funko especificado
            carrito_item = CarritoItem.objects.get(
                carrito=carrito, funko__idFunko=id_funko
            )

            # Actualizar el total en el carrito
            with transaction.atomic():
                carrito.total -= carrito_item.subtotal
                carrito_item.delete()
                carrito.save()

            return Response(
                {"Mensaje": "Funko eliminado del carrito correctamente."},
                status=status.HTTP_200_OK,
            )

        except Carrito.DoesNotExist:
            return Response(
                {"error": "Carrito no encontrado para el usuario."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except CarritoItem.DoesNotExist:
            return Response(
                {"error": "El Funko especificado no está en el carrito."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
                    "CarritoItems": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Carrito.DoesNotExist:
            return Response(
                {"error": "Carrito no encontrado para el usuario."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(["POST", "GET"])
@token_required
def compras(request, usuario):

    if request.method == "POST": 
        # DEPRECATED DO NOT USE
        # IF U USE THIS IM GOING TO FUCKING KILL YOU
        # ATTE MIRKO
        # Modificar esta logica, cuando se crea una compra se crea una direccion
        # Obtener el ID de la dirección desde el body de la request
        id_direccion = request.data.get("idDireccion")
        if not id_direccion:
            return Response(
                {"error": "Falta el ID de la dirección."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Obtener el carrito del usuario y verificar si contiene items
            carrito = Carrito.objects.get(usuario=usuario)
            carrito_items = CarritoItem.objects.filter(carrito=carrito)
            if not carrito_items.exists():
                return Response(
                    {"error": "El carrito está vacío."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Crear la compra con valores temporales de subtotal y total
            today = date.today()
            compra = Compra.objects.create(
                usuario=usuario,
                direccion_id=id_direccion,
                subtotal=0,  # Valor temporal
                total=0,  # Valor temporal
                fecha=today,
                estado="PENDIENTE",
            )

            # Variables para calcular el subtotal y total de la compra
            subtotal_compra = 0

            # Crear las líneas de compra (CompraItem) a partir de los items del carrito
            with transaction.atomic():
                for item in carrito_items:

                    # Verificar si hay suficiente stock
                    if item.funko.stock >= item.cantidad:
                        # Restar el stock del Funko
                        item.funko.stock -= item.cantidad
                        item.funko.save()
                        item.funko.refresh_from_db()  # Asegurar que el cambio se refleja en la BD
                        print(f"Nuevo stock de {item.funko.nombre}: {item.funko.stock}")

                    else:
                        return Response(
                            {"error": f"Stock insuficiente para el Funko {item.funko.nombre}."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Crear el CompraItem basado en cada CarritoItem
                    compra_item = CompraItem.objects.create(
                        compra=compra,
                        funko=item.funko,
                        cantidad=item.cantidad,
                        subtotal=item.subtotal,
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
                {"Mensaje": "Compra creada exitosamente.", "Compra": serializer.data, "idUsuario": usuario.idUsuario},
                status=status.HTTP_201_CREATED,
            )

        except Carrito.DoesNotExist:
            return Response(
                {"error": "Carrito no encontrado para el usuario."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(["PATCH", "GET"])
@token_required
def operaciones_compras(request, usuario, id):

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
                return Response(
                    {"error": "No tienes permiso para acceder a esta compra."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        except Compra.DoesNotExist:
            return Response(
                {"error": "Compra no encontrada."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    elif request.method == "PATCH":
        if not usuario.is_staff:
            # Solo los administradores pueden cambiar el estado de la compra
            return Response(
                {
                    "error": "Permiso denegado. Solo los administradores pueden cambiar el estado de una compra."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            # Obtener la compra
            compra = Compra.objects.get(idCompra=id)

            # Validar que el nuevo estado esté en los cambios permitidos
            nuevo_estado = request.data.get("estado")

            if nuevo_estado not in ["ENVIADO", "ENTREGADO"]:
                return Response(
                    {
                        "error": "El estado proporcionado no es válido. Solo se permite cambiar a 'ENVIADO' o 'ENTREGADO'."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Cambios permitidos de estado
            if compra.estado == "PENDIENTE" and nuevo_estado == "ENVIADO":
                compra.estado = "ENVIADO"
            elif compra.estado == "ENVIADO" and nuevo_estado == "ENTREGADO":
                compra.estado = "ENTREGADO"
            else:
                return Response(
                    {
                        "error": f"No se permite cambiar el estado de '{compra.estado}' a '{nuevo_estado}'."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Guardar el cambio de estado
            compra.save()

            # Serializar y retornar la compra actualizada
            serializer = CompraSerializer(compra)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Compra.DoesNotExist:
            return Response(
                {"error": "Compra no encontrada."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Codigo robado, esto no funciona todavia
#
# class ProcesoPagoAPIView(APIView):
#     def post(self, request):
#         try:
#             request_values = json.loads(request.body)
#             payment_data = {
#                 "transaction_amount": float(request_values["transaction_amount"]),
#                 "token": request_values["token"],
#                 "installments": int(request_values["installments"]),
#                 "payment_method_id": request_values["payment_method_id"],
#                 "issuer_id": request_values["issuer_id"],
#                 "payer": {
#                     "email": request_values["payer"]["email"],
#                     "identification": {
#                         "type": request_values["payer"]["identification"]["type"],
#                         "number": request_values["payer"]["identification"]["number"]
#                     }
#                 },

#             }

#             sdk = mercadopago.SDK(str(settings.MERCADOPAGO_ACCESS_TOKEN_TEST))

#             payment_response = sdk.payment().create(payment_data)

#             payment = payment_response["response"]
#             status = {
#                 "id": payment["id"],
#                 "status": payment["status"],
#                 "status_detail": payment["status_detail"],
#             }

#             return Response(
#                 data={"body": status, "statusCode": payment_response["status"]},
#                 status=201,
#             )
#         except Exception as e:
#    return Response(data={"body": payment_response}, status=400)


# Inicializa el cliente de MercadoPago con tu Access Token (clave privada)
sdk = mercadopago.SDK(
    settings.MERCADOPAGO_ACCESS_TOKEN_TEST
)  # Reemplaza con tu Access Token

""""
@api_view(["POST"])
@csrf_exempt
def CreatePreference(request, *args, **kwargs):
    # Datos de la preferencia
    preference_data = {
        "items": [
            {
                "title": "Funko Pop Spider-Man",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": 1.0,
            },
            {
                "title": "Funko Pop Iron Man",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": 1.0,
            },
            {
                "title": "Funko Pop Captain America",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": 1.0,
            },
            {
                "title": "Funko Pop Hulk",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": 1.0,
            },
            {
                "title": "Funko Pop Thor",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": 1.0,
            },
        ],
        "back_urls": {
            "success": "https://importfunko.netlify.app/dashboard.html",  # URL cuando el pago es exitoso
            "failure": "https://importfunko.netlify.app/dashboard.html",  # URL cuando el pago es rechazado
            "pending": "http://tu_dominio.com/pending",  # URL opcional para pagos pendientes
        },
    }

    # Crea la preferencia
    preference_response = sdk.preference().create(preference_data)
    preference_id = preference_response["response"]["id"]

    return JsonResponse({"preference_id": preference_id})


@api_view(["POST"])
@csrf_exempt
@token_required_without_user
def CreatePreferenceUser(request):
    # Datos de la preferencia
    preference_data = {
        "items": [
            {
                "title": "Funko Pop Spider-Man",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": 1.0,
            },
            {
                "title": "Funko Pop Iron Man",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": 1.0,
            },
            {
                "title": "Funko Pop Captain America",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": 1.0,
            },
            {
                "title": "Funko Pop Hulk",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": 1.0,
            },
            {
                "title": "Funko Pop Thor",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": 1.0,
            },
        ],
        "back_urls": {
            "success": "https://importfunko.netlify.app/dashboard.html",  # URL cuando el pago es exitoso
            "failure": "https://importfunko.netlify.app/dashboard.html",  # URL cuando el pago es rechazado
        },
    }

    # Crea la preferencia
    preference_response = sdk.preference().create(preference_data)
    preference_id = preference_response["response"]["id"]

    return JsonResponse({"preference_id": preference_id})
"""

# @api_view(["POST"])
# @token_required
# @csrf_exempt
# def CreatePreferenceFromCart(request, usuario):
#     try:

#         # Obtener el carrito del usuario
#         carrito = Carrito.objects.get(usuario=usuario)

#         # Obtener los ítems del carrito
#         carrito_items = CarritoItem.objects.filter(carrito=carrito)

#         # Crear la lista de ítems para MercadoPago
#         items_for_mp = []
#         for item in carrito_items:
#             funko = item.funko
#             item_data = {
#                 "title": funko.nombre,  # Nombre del funko
#                 "quantity": item.cantidad,  # Cantidad del ítem en el carrito
#                 "currency_id": "ARS",  # Moneda
#                 "unit_price": float(item.subtotal / item.cantidad),  # Precio unitario
#             }
#             items_for_mp.append(item_data)

#         # Datos de la preferencia
#         preference_data = {
#             "items": items_for_mp,
#             "back_urls": {
#                 "success": "https://importfunko.netlify.app/dashboard.html",
#                 "failure": "https://importfunko.netlify.app/dashboard.html",
#             },
#             "auto_return": "approved",
#         }

#         # Crear la preferencia en MercadoPago
#         preference_response = sdk.preference().create(preference_data)
#         preference_id = preference_response["response"]["id"]

#         return JsonResponse({"preference_id": preference_id})

#     except Carrito.DoesNotExist:
#         return Response(
#             {"error": "Carrito no encontrado para el usuario."},
#             status=status.HTTP_404_NOT_FOUND,
#         )
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@token_required
# @csrf_exempt
def CreatePreferenceFromCart(request, usuario):
    try:
        # Validate usuario
        if not usuario:
            return Response(
                {"error": "Usuario no proporcionado o inválido."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Obtener el carrito del usuario
        carrito = Carrito.objects.get(usuario=usuario)

        # Obtener los ítems del carrito
        carrito_items = CarritoItem.objects.filter(carrito=carrito)
        envio = request.data.get("envio")

        # Validar que el carrito no esté vacío
        if not carrito_items.exists():
            return Response(
                {"error": "El carrito está vacío."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Obtener direccion_id desde el request o el modelo
        direccion_id = request.data.get("direccion_id") # <- añadir direccion a envio de frontend
        if not direccion_id or envio is None:
            return Response(
                {"error": "direccion_id y envio es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Crear la lista de ítems para MercadoPago

        # for item in carrito_items:
        #     funko = item.funko
        #     item_data = {
        #         "title": funko.nombre,
        #         "quantity": item.cantidad,
        #         "currency_id": "ARS",
        #         "unit_price": float(item.subtotal / item.cantidad),
        #     }
        #     items_for_mp.append(item_data)
        today = date.today()
        items_for_mp = []
        for item in carrito_items:
            funko = item.funko
            precio_funko = funko.precio 

            # Verificar si hay un descuento activo para el funko
            descuento_activo = FunkoDescuento.objects.filter(
                funko=funko,
                fecha_inicio__lte=today,
                fecha_expiracion__gte=today
            ).first()

            if descuento_activo:
                descuento = Descuento.objects.get(
                    idDescuento=descuento_activo.descuento.idDescuento
                )
                precio_funko = precio_funko * (1 - (descuento.porcentaje / 100))

            item_data = {
                "title": funko.nombre,
                "quantity": item.cantidad ,
                "currency_id": "ARS",
                "unit_price": float(precio_funko),
            }
            items_for_mp.append(item_data)

        envio_value = float(envio)
        if envio > 0:  # Only append if envio is a positive value

            costo_envio = {
                "title": "Costo de Envío",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": envio_value,  # Use the envio value from frontend
            }

            if carrito.envio != 0:
                items_for_mp.append(costo_envio)
                diferenciaEnvios = carrito.envio - envio_value # 100 - 150
                carrito.envio = envio_value
                carrito.total = carrito.total - diferenciaEnvios # 200 - - 50  = 250
                carrito.save()
            else:
                items_for_mp.append(costo_envio)
                carrito.envio = envio_value
                carrito.total = carrito.total + envio_value
                carrito.save()

        # Encode carrito.id and direccion_id as JSON in external_reference
        external_reference = json.dumps(
            {"carrito_id": str(carrito.idCarrito), "direccion_id": str(direccion_id)}
        )

        # Validar longitud de external_reference
        if len(external_reference) > 256:
            direccion = Direccion.objects.get(direccion_id)
            direccion.delete()
            return Response(
                {"error": "External reference excede los 256 caracteres."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Datos de la preferencia
        preference_data = {
            "items": items_for_mp,
            "payer": {"email": usuario.email},
            "back_urls": {
                "success": "https://importfunko.vercel.app/thank-you",
                "failure": "https://importfunko.vercel.app/rejected",
                # "pending": "https://importfunko.netlify.app/dashboard.html", No pending i dont want to work
            },
            "auto_return": "approved",
            "notification_url": "https://practica-django-fxpz.onrender.com/webhook/mercado-pago/",  # A donde se manda la notificacion
            "external_reference": external_reference,
        }

        # Crear la preferencia en MercadoPago
        preference_response = sdk.preference().create(preference_data)
        if preference_response["status"] != 201:
            direccion = Direccion.objects.get(direccion_id)
            direccion.delete()
            return Response(
                {
                    "error": f"Error al crear la preferencia: {preference_response.get('message', 'Desconocido')}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        preference_id = preference_response["response"]["id"]
        return Response({"preference_id": preference_id}, status=status.HTTP_200_OK)

    except Carrito.DoesNotExist:
        return Response(
            {"error": "Carrito no encontrado para el usuario."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except mercadopago.exceptions.MPException as mp_error:
        return Response(
            {"error": f"Error de MercadoPago: {str(mp_error)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        print(f"Error en CreatePreferenceFromCart: {str(e)}")
        return Response(
            {"error": "Error interno del servidor."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@csrf_exempt
def mercado_pago_webhook(request):

    def getOAuth():
        # Define the API endpoint
        url = "https://api.mercadopago.com/oauth/token"

        # Define the JSON payload
        payload = {
            "client_secret": os.getenv("MERCADOPAGO_CLIENT_SECRET"),
            "client_id": os.getenv("MERCADOPAGO_CLIENT_ID"),
            "grant_type": "client_credentials",
        }

        # Define headers
        headers = {"Content-Type": "application/json"}

        try:
            # Make the POST request
            response = requests.post(url, json=payload, headers=headers)

            # Check if the request was successful
            response.raise_for_status()

            # Return the response as JSON
            return response.json()

        except Exception as e:
            return Response({"error": "Uncatched error"}, status=status.HTTP_200_OK)

    def refundLocalError(payment_id):
        try:
            url = f"https://api.mercadopago.com/v1/payments/{payment_id}/refunds"
            token_data =  getOAuth()
            access_token = token_data["access_token"]

            # Define headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Idempotency-Key": str(uuid.uuid4())
            }

            # Make the POST request (no body)
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            error_detail = response.json() if response.content else str(http_err)
            raise Exception(f"API error: {error_detail}")
        except requests.exceptions.RequestException as req_err:
            raise Exception(f"Request failed: {str(req_err)}")

    
    try:
        data = json.loads(request.body)
        signature = request.headers.get("x-signature", "")
        secret = os.getenv("MERCADOPAGO_SIGNING_SECRET")
        xRequestId = request.headers.get("x-request-id")

        mp_id = request.GET.get("data.id") or data.get('id') or request.GET.get("id")

        if not validate_signature(request.body, signature, secret, mp_id, xRequestId): # send mp_id here, remove logic to find it inside

            return Response(
                {
                    "error": f"Merchant orders son ignoradas"
                },
                status=status.HTTP_200_OK,
            )

        payload = json.loads(request.body.decode("utf-8"))
        topic = payload.get("topic") or payload.get("type")

        resource_id = payload.get("data", {}).get("id") or payload.get("id")
        if not resource_id:
            logger.error(f"No resource_id found in payload: {str(payload)}")
            return Response(
                {"error": "No resource_id found"},
                status=status.HTTP_200_OK,
            )

        if topic == "payment":
            payment_response = sdk.payment().get(resource_id)
            payment = payment_response["response"]
            payment_status = payment.get("status")
            external_reference = payment.get("external_reference", "")

            # Parse external_reference
            try:
                ref_data = json.loads(external_reference)
                carrito_id = ref_data.get("carrito_id")
                direccion_id = ref_data.get("direccion_id")
            except (json.JSONDecodeError, KeyError):
                logger.error(f"Invalid external_reference format: {external_reference}")
                return Response(
                    {"error": "Invalid external_reference format"},
                    status=status.HTTP_201_OK,
                )

            # Fetch and validate cart
            try:
                carrito = Carrito.objects.get(idCarrito = carrito_id)

            except Carrito.DoesNotExist:
                logger.error(f"Cart not found for carrito_id: {carrito_id}")
                return Response(
                    {"error": "Cart not found"},
                    status=status.HTTP_200_OK,
                )

            if payment_status == "approved":
                try:

                    # Verificar si el carrito tiene items
                    carrito_items = CarritoItem.objects.filter(carrito=carrito)
                    direccion = Direccion.objects.get(idDireccion=direccion_id)
                    user_email = direccion.email or carrito.usuario.email
                    if not carrito_items.exists():
                        refundLocalError(mp_id)
                        direccion.delete()
                        send_email(
                            to=user_email,
                            subject="Error en la compra",
                            body=f"No se pudo procesar tu compra (ID de Mercado Pago: {mp_id}) porque el carrito está vacío.Se ha devuelto su pago .Comunicate a nuestro email con el Mercado Pago ID",
                        )
                        return Response(
                            {"error": "Empty cart."},
                            status=status.HTTP_201_OK,
                        )

                    # Crear la compra con valores temporales de subtotal y total

                    # Crear las líneas de compra (CompraItem) a partir de los items del carrito
                    with transaction.atomic():

                        today = date.today()
                        compra = Compra.objects.create(
                            usuario=carrito.usuario,
                            direccion=direccion,
                            subtotal=0,  # Valor temporal
                            total=0,  # Valor temporal
                            fecha=today,
                            estado="PENDIENTE",
                        )

                        # Variables para calcular el subtotal y total de la compra
                        subtotal_compra = 0
                        for item in carrito_items:
                            # Verificar si hay suficiente stock
                            if item.funko.stock >= item.cantidad:
                                # Restar el stock del Funko
                                item.funko.stock -= item.cantidad
                                item.funko.save()
                                # item.funko.refresh_from_db()

                            else:
                                direccion.delete()
                                send_email(
                                    to=user_email,
                                    subject="Error en la compra",
                                    body=f"No se pudo procesar tu compra (ID de Mercado Pago: {mp_id}) debido a stock insuficiente para el Funko {item.funko.nombre}. Se ha devuelto su pago.Comunicate a nuestro email con el Mercado Pago ID",
                                )
                                refundLocalError(mp_id)
                                return Response(
                                    {
                                        "error": f"Stock insuficiente para el Funko {item.funko.nombre}."
                                    },
                                    status=status.HTTP_200_OK,
                                )

                            # add something like this
                            descuento_activo = FunkoDescuento.objects.filter(
                                funko=item.funko, fecha_inicio__lte=today, fecha_expiracion__gte=today
                            ).first()

                            if descuento_activo:
                                descuento = Descuento.objects.get(
                                    idDescuento=descuento_activo.descuento.idDescuento
                                )

                                precio_funko = item.funko.precio * ( 1 - (descuento.porcentaje / 100))
                            else:
                                precio_funko = item.funko.precio
                            # Crear el CompraItem basado en cada CarritoItem

                            compra_item = CompraItem.objects.create(
                                compra=compra,
                                funko=item.funko,
                                cantidad=item.cantidad,
                                subtotal=precio_funko * item.cantidad,  # Change this to validate discount
                            )
                            # Sumar el subtotal del item al subtotal total de la compra
                            subtotal_compra += compra_item.subtotal

                        # Actualizar subtotal y total en la compra
                        compra.subtotal = subtotal_compra
                        compra.total = compra.subtotal + carrito.envio
                        compra.envio = carrito.envio
                        compra.save()

                        # Limpiar el carrito después de crear la compra
                        carrito.items.all().delete()  # Eliminar todos los CarritoItems
                        carrito.total = 0  # Reiniciar el total del carrito
                        carrito.envio = 0  # Reinicia el envio del carrito
                        carrito.save()

                    # Serializar y devolver la compra creada
                    serializer = CompraSerializer(compra)
                    send_email(
                        to=user_email,
                        subject="Compra realizada con éxito",
                        body=f"Tu compra con ID {compra.idCompra} (ID de Mercado Pago: {mp_id}) ha sido procesada exitosamente. Total: ${compra.total}",
                        html_template="emails/purchase_confirmation.html",
                        context={
                            "message": f"Tu compra con ID {compra.idCompra} (ID de Mercado Pago: {mp_id}) ha sido procesada exitosamente.",
                            "compra": compra,
                            "mp_id": mp_id
                        }
                    )
                    return Response(
                        {
                            "Mensaje": "Compra creada exitosamente.",
                            "Compra": serializer.data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                except Exception as e:
                    direccion.delete()
                    refundLocalError(mp_id)
                    send_email(
                        to=user_email,
                        subject="Error en la compra",
                        body=f"No se pudo procesar tu compra (ID de Mercado Pago: {mp_id}) debido a un error: {str(e)}.Se ha devuelto su pago.Comunicate a nuestro email con el Mercado Pago ID",
                    )
                    return Response(
                        {"error": f"Purchase creation failed: {str(e)}"},
                        status=status.HTTP_201_CREATED,
                    )

            elif payment_status == "pending":
                return Response({"status": "Pending"}, status=status.HTTP_200_OK)
            elif payment_status == "cancelled":
                direccion.delete()
                send_email(
                    to=user_email,
                    subject="Compra cancelada",
                    body=f"Tu compra (ID de Mercado Pago: {mp_id}) ha sido cancelada. Comunicate a nuestro email con el Mercado Pago ID",
                )
                return Response(
                    {"error": f"Payment {payment_status}"},
                    status=status.HTTP_200_OK,
                )
            elif payment == "refunded":
                pass

        return Response({"error": f"{str(signature)}   {str(secret)}   {str(xRequestId)}    {str(mp_id)}      {str(request.body)}    {str(request.headers)}"},
                        status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        try:
            carrito = Carrito.objects.get(idCarrito=carrito_id) if 'carrito_id' in locals() else None
            if carrito:
                email = direccion.email or carrito.usuario.email
                send_email(
                    to=email,
                    subject="Error en el procesamiento",
                    body=f"Se produjo un error inesperado al procesar tu solicitud (ID de Mercado Pago: {mp_id}): {str(e)}. Comunicate a nuestro email con el Mercado Pago ID",
                )
        except:
            pass
        return Response({"error": "Uncatched error"}, status=status.HTTP_200_OK)

# New atrbute on carrito and compra for shipment price
# Only add shipment price
