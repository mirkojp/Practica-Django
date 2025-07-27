# from django.shortcuts import get_object_or_404
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from django.db import transaction
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import requests
# import json
# from .models import Provincia, Ciudad, Coordenada, Direccion
# from .serializers import (
#     DireccionSerializer,
#     CoordenadaSerializer,
#     CiudadSerializer,
#     ProvinciaSerializer,
# )
# from .services import obtener_info_georef, obtener_info_google_maps
# from django.conf import settings

# class DireccionViewSet(viewsets.ViewSet):
#     """
#     ViewSet para manejar operaciones CRUD de Direccion.
#     """

#     def list(self, request):
#         """
#         GET: Lista todas las direcciones.
#         """
#         direcciones = Direccion.objects.select_related(
#             "ciudad__provincia", "coordenada"
#         ).all()
#         serializer = DireccionSerializer(direcciones, many=True)
#         return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         """
#         GET: Obtiene una dirección específica por su ID.
#         """
#         direccion = get_object_or_404(
#             Direccion.objects.select_related("ciudad__provincia", "coordenada"),
#             idDireccion=pk,
#         )
#         serializer = DireccionSerializer(direccion)
#         return Response(serializer.data)

#     def update(self, request, pk=None):
#         """
#         PUT: Actualiza una dirección existente.
#         """
#         direccion = get_object_or_404(Direccion, idDireccion=pk)
#         data = request.data

#         try:
#             with transaction.atomic():
#                 # Actualizar coordenada
#                 coordenada_data = data.get("coordenada", {})
#                 coordenada_serializer = CoordenadaSerializer(
#                     instance=direccion.coordenada, data=coordenada_data, partial=True
#                 )
#                 if coordenada_serializer.is_valid():
#                     coordenada_serializer.save()
#                 else:
#                     return Response(
#                         coordenada_serializer.errors, status=status.HTTP_400_BAD_REQUEST
#                     )

#                 # Actualizar ciudad y provincia
#                 ciudad_data = data.get("ciudad", {})
#                 provincia_data = ciudad_data.get("provincia", {})
#                 provincia_nombre = provincia_data.get("nombre")

#                 if provincia_nombre:
#                     provincia = get_object_or_404(Provincia, nombre=provincia_nombre)
#                     ciudad_nombre = ciudad_data.get("nombre")
#                     if ciudad_nombre:
#                         ciudad, _ = Ciudad.objects.get_or_create(
#                             nombre=ciudad_nombre, provincia=provincia
#                         )
#                     else:
#                         return Response(
#                             {"error": "Nombre de ciudad es requerido"},
#                             status=status.HTTP_400_BAD_REQUEST,
#                         )
#                 else:
#                     ciudad = direccion.ciudad

#                 # Actualizar dirección
#                 direccion_data = {
#                     "calle": data.get("calle", direccion.calle),
#                     "numero": data.get("numero", direccion.numero),
#                     "piso": data.get("piso", direccion.piso),
#                     "depto": data.get("depto", direccion.depto),
#                     "codigo_postal": data.get("codigo_postal", direccion.codigo_postal),
#                     "contacto": data.get("contacto", direccion.contacto),
#                     "email": data.get("email", direccion.email),
#                     "ciudad": ciudad.idCiudad,
#                     "coordenada": direccion.coordenada.idCoordenada,
#                 }
#                 serializer = DireccionSerializer(
#                     instance=direccion, data=direccion_data, partial=True
#                 )
#                 if serializer.is_valid():
#                     serializer.save()
#                     return Response(serializer.data)
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     def destroy(self, request, pk=None):
#         """
#         DELETE: Elimina una dirección por su ID.
#         """
#         direccion = get_object_or_404(Direccion, idDireccion=pk)
#         try:
#             with transaction.atomic():
#                 # Eliminar la coordenada asociada
#                 if direccion.coordenada:
#                     direccion.coordenada.delete()
#                 direccion.delete()
#                 return Response(
#                     {"message": "Dirección eliminada correctamente"},
#                     status=status.HTTP_204_NO_CONTENT,
#                 )
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# # Funciones existentes (mantenidas para compatibilidad)
# def obtener_info_ubicacion(request):
#     """Recibe latitud/longitud, consulta Google Maps API y almacena los datos en la sesión."""
#     if request.method == "POST":
#         data = json.loads(request.body)
#         lat = data.get("lat")
#         lon = data.get("lon")

#         if not lat or not lon:
#             return JsonResponse({"error": "Faltan coordenadas"}, status=400)

#         # Obtener datos de Google Maps
#         data_google = obtener_info_google_maps(lat, lon)

#         # Guardar en la sesión para futuras validaciones
#         request.session["google_data"] = data_google

#         return JsonResponse(
#             {"coordenadas": {"latitud": lat, "longitud": lon}, "google": data_google}
#         )


# def guardar_direccion(request):
#     if request.method == "POST":
#         data = json.loads(request.body)

#         # Extraer datos de Google Maps
#         calle = data["google"]["calle"]
#         numero = data["google"]["numero"]
#         codigo_postal = data["google"]["cp"]
#         contacto = data.get("contacto")  # Puede ser opcional
#         email = data.get("email")  # Puede ser opcional
#         lat = data["google"]["lat"]
#         lon = data["google"]["lon"]

#         # Extraer nombres de ciudad y provincia desde Google Maps
#         nombre_provincia = data["google"]["provincia"]
#         nombre_ciudad = data["google"]["ciudad"]

#         with transaction.atomic():
#             provincia = get_object_or_404(Provincia, nombre=nombre_provincia)

#             ciudad, _ = Ciudad.objects.get_or_create(
#                 nombre=nombre_ciudad, provincia=provincia
#             )

#             coordenada = Coordenada.objects.create(latitud=lat, longitud=lon)

#             direccion = Direccion.objects.create(
#                 calle=calle,
#                 numero=numero,
#                 codigo_postal=codigo_postal,
#                 contacto=contacto,
#                 email=email,
#                 coordenada=coordenada,
#                 ciudad=ciudad,
#             )

#         return JsonResponse(
#             {
#                 "message": "Dirección guardada correctamente",
#                 "id_direccion": direccion.idDireccion,
#             }
#         )


# @csrf_exempt
# def obtener_direccion(request, id_direccion):
#     if request.method == "GET":
#         direccion = get_object_or_404(
#             Direccion.objects.select_related("ciudad", "coordenada"),
#             idDireccion=id_direccion,
#         )

#         data = {
#             "id_direccion": direccion.idDireccion,
#             "calle": direccion.calle,
#             "numero": direccion.numero,
#             "piso": direccion.piso,
#             "depto": direccion.depto,
#             "codigo_postal": direccion.codigo_postal,
#             "contacto": str(direccion.contacto) if direccion.contacto else None,
#             "email": direccion.email,
#             "coordenada": {
#                 "latitud": direccion.coordenada.latitud,
#                 "longitud": direccion.coordenada.longitud,
#             },
#             "ciudad": direccion.ciudad.nombre,
#             "provincia": direccion.ciudad.provincia.nombre,
#         }
#         return JsonResponse(data)

#     return JsonResponse({"error": "Método no permitido"}, status=405)


# def recalcular_y_guardar_direccion(request):
#     """
#     Recibe datos del frontend, verifica si calle o número fueron modificados,
#     recalcula coordenadas si es necesario y guarda/actualiza la dirección.
#     """
#     if request.method == "POST":
#         data = json.loads(request.body)
#         lat = data.get("lat")
#         lon = data.get("lon")
#         calle = data.get("calle")
#         numero = data.get("numero")
#         codigo_postal = data.get("codigo_postal")
#         contacto = data.get("contacto")
#         email = data.get("email")
#         nombre_ciudad = data.get("ciudad")
#         nombre_provincia = data.get("provincia")
#         id_direccion = data.get("id_direccion")  # Opcional, para actualizar

#         if (
#             not lat
#             or not lon
#             or not calle
#             or not numero
#             or not nombre_ciudad
#             or not nombre_provincia
#         ):
#             return JsonResponse({"error": "Faltan datos requeridos"}, status=400)

#         # Obtener datos originales de Google Maps para comparar
#         data_google = obtener_info_google_maps(lat, lon)
#         if not data_google:
#             return JsonResponse({"error": "Error al consultar Google Maps"}, status=400)

#         # Verificar si calle o número fueron modificados
#         calle_modificada = calle != data_google.get("calle")
#         numero_modificado = numero != data_google.get("numero")

#         # Si calle o número fueron modificados, recalcular coordenadas
#         if calle_modificada or numero_modificado:
#             # Construir la dirección para geocodificación
#             direccion_completa = (
#                 f"{calle} {numero}, {nombre_ciudad}, {nombre_provincia}, Argentina"
#             )
#             url = f"https://maps.googleapis.com/maps/api/geocode/json?address={direccion_completa}&key={settings.GOOGLE_MAPS_API_KEY}"
#             response = requests.get(url)

#             if response.status_code == 200 and response.json().get("status") == "OK":
#                 result = response.json()["results"][0]
#                 lat = result["geometry"]["location"]["lat"]
#                 lon = result["geometry"]["location"]["lng"]
#             else:
#                 return JsonResponse(
#                     {"error": "Error al recalcular coordenadas"}, status=400
#                 )

#         try:
#             with transaction.atomic():
#                 # Obtener o crear provincia
#                 provincia = get_object_or_404(Provincia, nombre=nombre_provincia)

#                 # Obtener o crear ciudad
#                 ciudad, _ = Ciudad.objects.get_or_create(
#                     nombre=nombre_ciudad, provincia=provincia
#                 )

#                 if id_direccion:
#                     # Actualizar dirección existente
#                     direccion = get_object_or_404(Direccion, idDireccion=id_direccion)
#                     direccion.calle = calle
#                     direccion.numero = numero
#                     direccion.codigo_postal = codigo_postal
#                     direccion.contacto = contacto
#                     direccion.email = email
#                     direccion.ciudad = ciudad
#                     # Actualizar coordenadas
#                     direccion.coordenada.latitud = lat
#                     direccion.coordenada.longitud = lon
#                     direccion.coordenada.save()
#                     direccion.save()
#                 else:
#                     # Crear nueva dirección
#                     coordenada = Coordenada.objects.create(latitud=lat, longitud=lon)
#                     direccion = Direccion.objects.create(
#                         calle=calle,
#                         numero=numero,
#                         codigo_postal=codigo_postal,
#                         contacto=contacto,
#                         email=email,
#                         coordenada=coordenada,
#                         ciudad=ciudad,
#                     )

#                 return JsonResponse(
#                     {
#                         "message": "Dirección procesada correctamente",
#                         "id_direccion": direccion.idDireccion,
#                         "coordenadas": {"latitud": lat, "longitud": lon},
#                     }
#                 )

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=400)

#     return JsonResponse({"error": "Método no permitido"}, status=405)


# View traer sucursales
# Añadir Depto y piso en models.direccion
# GET, PUT, DELETE de direccion
from datetime import timedelta
from django.utils import timezone
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from requests import Response
from decorators.token_decorators import token_required_without_user, token_required_admin_without_user
from rest_framework.decorators import (
    api_view,

)
from phonenumber_field.phonenumber import PhoneNumber

from rest_framework import status
from .models import Direccion, Ciudad, Provincia
from .serializers import DireccionSerializer

import json


@api_view(["POST"])
@token_required_without_user
def crear_direccion(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Validate required fields
            required_fields = [
                "calle",
                "numero",
                "codigo_postal",
                "ciudad",
                "provincia",
            ]
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse(
                        {"error": f"El campo {field} es obligatorio"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            # Get Provincia by name
            try:
                provincia = Provincia.objects.get(nombre=data["provincia"])
            except Provincia.DoesNotExist:
                return JsonResponse(
                    {"error": "Provincia no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            # Get or create Ciudad
            ciudad, created = Ciudad.objects.get_or_create(
                nombre=data["ciudad"],
                provincia=provincia,
                defaults={"nombre": data["ciudad"], "provincia": provincia},
            )

            # Prepare serializer data
            serializer_data = {
                "calle": data["calle"],
                "numero": data["numero"],
                "codigo_postal": data["codigo_postal"],
                "ciudad":ciudad.nombre,
                "ciudad_id": ciudad.idCiudad,
                "piso": data.get("piso", ""),
                "depto": data.get("depto", ""),
                "email": data.get("email", ""),
            }

            # Handle phone number
            if data.get("contacto"):
                try:
                    contacto = PhoneNumber.from_string(data["contacto"], region="AR")
                    if not contacto.is_valid():
                        return JsonResponse(
                            {"error": "Número de teléfono inválido"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    serializer_data["contacto"] = str(contacto)
                except Exception:
                    return JsonResponse(
                        {"error": "Formato de número de teléfono inválido"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Use serializer for validation and creation
            serializer = DireccionSerializer(data=serializer_data)
            if serializer.is_valid():
                direccion = serializer.save()

                # Prepare response
                response_data = {
                    "id_direccion": direccion.idDireccion,
                    "calle": direccion.calle,
                    "numero": direccion.numero,
                    "piso": direccion.piso,
                    "depto": direccion.depto,
                    "codigo_postal": direccion.codigo_postal,
                    "contacto": str(direccion.contacto) if direccion.contacto else None,
                    "email": direccion.email,
                    "ciudad": direccion.ciudad.nombre,
                    "provincia": direccion.ciudad.provincia.nombre,
                }
                return JsonResponse(response_data, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse(
                    {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                )

        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Cuerpo de la solicitud inválido"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse(
                {"error": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return JsonResponse(
        {"error": "Método no permitido"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


@csrf_exempt
@api_view(["GET"])
@token_required_without_user
def obtener_direccion(request, id):
    if request.method == "GET":
        try:
            direccion = Direccion.objects.select_related("ciudad__provincia").get(
                idDireccion=id
            )

            # Use serializer for response
            serializer = DireccionSerializer(direccion)
            response_data = {
                "id_direccion": direccion.idDireccion,
                "calle": direccion.calle,
                "numero": direccion.numero,
                "piso": direccion.piso,
                "depto": direccion.depto,
                "codigo_postal": direccion.codigo_postal,
                "contacto": str(direccion.contacto) if direccion.contacto else None,
                "email": direccion.email,
                "ciudad": direccion.ciudad.nombre,
                "provincia": direccion.ciudad.provincia.nombre,
            }
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Direccion.DoesNotExist:
            return JsonResponse(
                {"error": "Dirección no encontrada"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception:
            return JsonResponse(
                {"error": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return JsonResponse(
        {"error": "Método no permitido"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


@api_view(["GET"])
@token_required_admin_without_user
def obtener_todas_direcciones(request):
    if request.method == "GET":
        try:
            # Retrieve all Direccion objects with related ciudad and provincia
            direcciones = Direccion.objects.select_related("ciudad__provincia").all()

            # Prepare response data
            response_data = [
                {
                    "id_direccion": direccion.idDireccion,
                    "calle": direccion.calle,
                    "numero": direccion.numero,
                    "piso": direccion.piso,
                    "depto": direccion.depto,
                    "codigo_postal": direccion.codigo_postal,
                    "contacto": str(direccion.contacto) if direccion.contacto else None,
                    "email": direccion.email,
                    "ciudad": direccion.ciudad.nombre,
                    "provincia": direccion.ciudad.provincia.nombre,
                }
                for direccion in direcciones
            ]

            return JsonResponse(response_data, safe=False, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse(
                {"error": "Error interno del servidor", "detalle": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return JsonResponse(
        {"error": "Método no permitido"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


logger = logging.getLogger(__name__)


def obtener_direcciones_sin_compra_antiguas(request):
    if request.method == "GET":
        try:
            thirty_minutes_ago = timezone.now() - timedelta(minutes=30)
            direcciones = Direccion.objects.select_related("ciudad__provincia").filter(
                compra__isnull=True, creada__lt=thirty_minutes_ago
            )
            response_data = [
                {
                    "id_direccion": direccion.idDireccion,
                    "calle": direccion.calle,
                    "numero": direccion.numero,
                    "piso": direccion.piso,
                    "depto": direccion.depto,
                    "codigo_postal": direccion.codigo_postal,
                    "contacto": str(direccion.contacto) if direccion.contacto else None,
                    "email": direccion.email,
                    "ciudad": direccion.ciudad.nombre,
                    "provincia": direccion.ciudad.provincia.nombre,
                    "creada": direccion.creada.strftime("%Y-%m-%d %H:%M:%S %Z"),
                }
                for direccion in direcciones
            ]
            return JsonResponse(response_data, safe=False, status=200)
        except Exception as e:
            logger.error(f"Error retrieving Direccion objects: {str(e)}")
            return JsonResponse(
                {"error": "Error interno del servidor", "detalle": str(e)}, status=500
            )
    return JsonResponse({"error": "Método no permitido"}, status=405)


def eliminar_direcciones_sin_compra_antiguas(request):
    if request.method == "DELETE":
        try:
            thirty_minutes_ago = timezone.now() - timedelta(minutes=30)
            direcciones = Direccion.objects.filter(
                compra__isnull=True, creada__lt=thirty_minutes_ago
            )
            count = direcciones.count()
            deleted_ids = [direccion.idDireccion for direccion in direcciones]
            direcciones.delete()
            logger.info(
                f"Deleted {count} Direccion objects without Compra, older than 30 minutes: {deleted_ids}"
            )
            return JsonResponse(
                {
                    "message": f"Se eliminaron {count} direcciones sin compras asociadas y con más de 30 minutos de antigüedad.",
                    "deleted_ids": deleted_ids,
                },
                status=200,
            )
        except Exception as e:
            logger.error(f"Error deleting Direccion objects: {str(e)}")
            return JsonResponse(
                {"error": "Error interno del servidor", "detalle": str(e)}, status=500
            )
    return JsonResponse({"error": "Método no permitido"}, status=405)
