from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from .models import Provincia, Ciudad, Coordenada, Direccion
from .serializers import (
    DireccionSerializer,
    CoordenadaSerializer,
    CiudadSerializer,
    ProvinciaSerializer,
)
from .services import obtener_info_georef, obtener_info_google_maps


class DireccionViewSet(viewsets.ViewSet):
    """
    ViewSet para manejar operaciones CRUD de Direccion.
    """

    def list(self, request):
        """
        GET: Lista todas las direcciones.
        """
        direcciones = Direccion.objects.select_related(
            "ciudad__provincia", "coordenada"
        ).all()
        serializer = DireccionSerializer(direcciones, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET: Obtiene una dirección específica por su ID.
        """
        direccion = get_object_or_404(
            Direccion.objects.select_related("ciudad__provincia", "coordenada"),
            idDireccion=pk,
        )
        serializer = DireccionSerializer(direccion)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        PUT: Actualiza una dirección existente.
        """
        direccion = get_object_or_404(Direccion, idDireccion=pk)
        data = request.data

        try:
            with transaction.atomic():
                # Actualizar coordenada
                coordenada_data = data.get("coordenada", {})
                coordenada_serializer = CoordenadaSerializer(
                    instance=direccion.coordenada, data=coordenada_data, partial=True
                )
                if coordenada_serializer.is_valid():
                    coordenada_serializer.save()
                else:
                    return Response(
                        coordenada_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

                # Actualizar ciudad y provincia
                ciudad_data = data.get("ciudad", {})
                provincia_data = ciudad_data.get("provincia", {})
                provincia_nombre = provincia_data.get("nombre")

                if provincia_nombre:
                    provincia = get_object_or_404(Provincia, nombre=provincia_nombre)
                    ciudad_nombre = ciudad_data.get("nombre")
                    if ciudad_nombre:
                        ciudad, _ = Ciudad.objects.get_or_create(
                            nombre=ciudad_nombre, provincia=provincia
                        )
                    else:
                        return Response(
                            {"error": "Nombre de ciudad es requerido"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                else:
                    ciudad = direccion.ciudad

                # Actualizar dirección
                direccion_data = {
                    "calle": data.get("calle", direccion.calle),
                    "numero": data.get("numero", direccion.numero),
                    "piso": data.get("piso", direccion.piso),
                    "depto": data.get("depto", direccion.depto),
                    "codigo_postal": data.get("codigo_postal", direccion.codigo_postal),
                    "contacto": data.get("contacto", direccion.contacto),
                    "email": data.get("email", direccion.email),
                    "ciudad": ciudad.idCiudad,
                    "coordenada": direccion.coordenada.idCoordenada,
                }
                serializer = DireccionSerializer(
                    instance=direccion, data=direccion_data, partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        DELETE: Elimina una dirección por su ID.
        """
        direccion = get_object_or_404(Direccion, idDireccion=pk)
        try:
            with transaction.atomic():
                # Eliminar la coordenada asociada
                if direccion.coordenada:
                    direccion.coordenada.delete()
                direccion.delete()
                return Response(
                    {"message": "Dirección eliminada correctamente"},
                    status=status.HTTP_204_NO_CONTENT,
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Funciones existentes (mantenidas para compatibilidad)
def obtener_info_ubicacion(request):
    """Recibe latitud/longitud, consulta Google Maps API y almacena los datos en la sesión."""
    if request.method == "POST":
        data = json.loads(request.body)
        lat = data.get("lat")
        lon = data.get("lon")

        if not lat or not lon:
            return JsonResponse({"error": "Faltan coordenadas"}, status=400)

        # Obtener datos de Google Maps
        data_google = obtener_info_google_maps(lat, lon)

        # Guardar en la sesión para futuras validaciones
        request.session["google_data"] = data_google

        return JsonResponse(
            {"coordenadas": {"latitud": lat, "longitud": lon}, "google": data_google}
        )


def guardar_direccion(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # Extraer datos de Google Maps
        calle = data["google"]["calle"]
        numero = data["google"]["numero"]
        codigo_postal = data["google"]["cp"]
        contacto = data.get("contacto")  # Puede ser opcional
        email = data.get("email")  # Puede ser opcional
        lat = data["google"]["lat"]
        lon = data["google"]["lon"]

        # Extraer nombres de ciudad y provincia desde Google Maps
        nombre_provincia = data["google"]["provincia"]
        nombre_ciudad = data["google"]["ciudad"]

        with transaction.atomic():
            provincia = get_object_or_404(Provincia, nombre=nombre_provincia)

            ciudad, _ = Ciudad.objects.get_or_create(
                nombre=nombre_ciudad, provincia=provincia
            )

            coordenada = Coordenada.objects.create(latitud=lat, longitud=lon)

            direccion = Direccion.objects.create(
                calle=calle,
                numero=numero,
                codigo_postal=codigo_postal,
                contacto=contacto,
                email=email,
                coordenada=coordenada,
                ciudad=ciudad,
            )

        return JsonResponse(
            {
                "message": "Dirección guardada correctamente",
                "id_direccion": direccion.idDireccion,
            }
        )


@csrf_exempt
def obtener_direccion(request, id_direccion):
    if request.method == "GET":
        direccion = get_object_or_404(
            Direccion.objects.select_related("ciudad", "coordenada"),
            idDireccion=id_direccion,
        )

        data = {
            "id_direccion": direccion.idDireccion,
            "calle": direccion.calle,
            "numero": direccion.numero,
            "piso": direccion.piso,
            "depto": direccion.depto,
            "codigo_postal": direccion.codigo_postal,
            "contacto": str(direccion.contacto) if direccion.contacto else None,
            "email": direccion.email,
            "coordenada": {
                "latitud": direccion.coordenada.latitud,
                "longitud": direccion.coordenada.longitud,
            },
            "ciudad": direccion.ciudad.nombre,
            "provincia": direccion.ciudad.provincia.nombre,
        }
        return JsonResponse(data)

    return JsonResponse({"error": "Método no permitido"}, status=405)


# View traer sucursales
# Añadir Depto y piso en models.direccion
# GET, PUT, DELETE de direccion
