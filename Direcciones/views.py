from django.shortcuts import get_object_or_404
from rest_framework import viewsets
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import DireccionSerializer
from .models import Direccion
from django.db import transaction
# from .utils import obtener_o_crear_direccion
from django.http import JsonResponse
from .exceptions import EntityNotFoundError
from django.views.decorators.http import require_POST
from Compras.models import Compra
from decorators.token_decorators import token_required_without_user
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services import obtener_info_georef,obtener_info_google_maps
import json
from .models import Provincia, Ciudad, Coordenada, Direccion
from django.views.decorators.csrf import csrf_exempt

# @api_view(["GET"])
# @token_required_without_user
# def obtener_provincias(request):
#     """
#     Obtiene la lista de provincias desde la API de Georef.

#     Ejemplo de uso:
#     GET http://localhost:8000/obtener_provincias
#     """
#     url = "https://apis.datos.gob.ar/georef/api/provincias"

#     try:
#         response = requests.get(url)
#         response.raise_for_status()

#         if "provincias" in response.json():
#             return Response(response.json()["provincias"], status=status.HTTP_200_OK)
#         else:
#             return Response({"error": "No se encontraron provincias en la respuesta."}, status=status.HTTP_404_NOT_FOUND)

#     except requests.exceptions.HTTPError as http_err:
#         return Response(
#             {"error": f"Error HTTP: {http_err}"}, status=response.status_code
#         )
#     except requests.exceptions.RequestException as req_err:
#         return Response({"error": f"Error en la conexión: {req_err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     except Exception as e:
#         return Response(
#             {"error": f"Error inesperado: {e}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @token_required_without_user
# def localidades_por_provincia(request, id_provincia):
#     """
#     Obtiene localidades de una provincia específica filtradas por nombre.

#     Parámetros de consulta:
#     - localidad: Nombre de la localidad a buscar (requerido).
#     - max: Límite máximo de localidades a devolver (opcional, predeterminado 100).

#     Ejemplo de uso:
#     GET http://localhost:8000/localidades/30/?localidad=san&max=100
#     """

#     localidad = request.query_params.get("localidad", "")
#     if not localidad:
#         return Response(
#             {"error": "El parámetro 'localidad' no puede estar vacío."}, status=status.HTTP_400_BAD_REQUEST
#         )

#     # Validar el parámetro max
#     max_localidades_str = request.query_params.get("max", 100)
#     try:
#         max_localidades = int(max_localidades_str)
#         if max_localidades <= 0:
#             return Response(
#                 {"error": "'max' debe ser un número entero positivo."}, status=status.HTTP_400_BAD_REQUEST)
#     except ValueError:
#         return Response({"error": "'max' debe ser un número entero."}, status=status.HTTP_400_BAD_REQUEST)

#     url = (
#         f"https://apis.datos.gob.ar/georef/api/localidades?"
#         f"provincia={id_provincia}&nombre={localidad}&max={max_localidades}&aplanar=true&campos=basico"
#     )

#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Lanza un error para respuestas no exitosas
#         localidades = response.json().get("localidades", [])

#         return Response({"localidades": localidades}, status=status.HTTP_200_OK)

#     except requests.exceptions.HTTPError as http_err:
#         return Response(
#             {"error": f"Error HTTP: {http_err}"}, status=response.status_code
#         )
#     except requests.exceptions.RequestException as req_err:
#         return Response({"error": f"Error en la conexión: {req_err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     except Exception as e:
#         return Response(
#             {"error": f"Error inesperado: {e}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @token_required_without_user
# def localidades_censales_por_provincia(request, id_provincia):
#     """
#     Obtiene localidades censales de una provincia específica filtradas por nombre.

#     Parámetros de consulta:
#     - localidad: Nombre de la localidad censal a buscar (requerido).
#     - max: Límite máximo de localidades censales a devolver (opcional, predeterminado 100).

#     Ejemplo de uso:
#     GET http://localhost:8000/localidades-censales/30/?localidad=san&max=100
#     """

#     localidad = request.query_params.get("localidad", "")
#     if not localidad:
#         return Response(
#             {"error": "El parámetro 'localidad' no puede estar vacío."},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     # Validar el parámetro max
#     max_localidades_str = request.query_params.get("max", 100)
#     try:
#         max_localidades = int(max_localidades_str)
#         if max_localidades <= 0:
#             return Response(
#                 {"error": "'max' debe ser un número entero positivo."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#     except ValueError:
#         return Response(
#             {"error": "'max' debe ser un número entero."},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     # Cambiamos la URL para consultar localidades censales en lugar de localidades normales
#     url = (
#         f"https://apis.datos.gob.ar/georef/api/localidades-censales?"
#         f"provincia={id_provincia}&nombre={localidad}&max={max_localidades}&aplanar=true&campos=basico"
#     )

#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Lanza un error para respuestas no exitosas
#         localidades_censales = response.json().get("localidades_censales", [])

#         return Response(
#             {"localidades_censales": localidades_censales}, status=status.HTTP_200_OK
#         )

#     except requests.exceptions.HTTPError as http_err:
#         return Response(
#             {"error": f"Error HTTP: {http_err}"}, status=response.status_code
#         )
#     except requests.exceptions.RequestException as req_err:
#         return Response(
#             {"error": f"Error en la conexión: {req_err}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )
#     except Exception as e:
#         return Response(
#             {"error": f"Error inesperado: {e}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["GET"])
# @token_required_without_user
# def calles_por_localidad_censal(request, id_provincia, id_localidad_censal):
#     """
#     Obtiene calles de una localidad censal específica filtradas por nombre.

#     Parámetros de consulta:
#     - calle: Nombre de la calle a buscar (requerido).
#     - max: Límite máximo de calles a devolver (opcional, predeterminado 100).

#     Ejemplo de uso:
#     GET http://localhost:8000/calles/30/30088020/?calle=paoloni&max=100
#     """

#     calle = request.query_params.get("calle", "")
#     if not calle:
#         return Response(
#             {"error": "El parámetro 'calle' no puede estar vacío."},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     # Validar el parámetro max
#     max_calles_str = request.query_params.get("max", 100)
#     try:
#         max_calles = int(max_calles_str)
#         if max_calles <= 0:
#             return Response(
#                 {"error": "'max' debe ser un número entero positivo."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#     except ValueError:
#         return Response(
#             {"error": "'max' debe ser un número entero."},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     # Construimos la URL para consultar las calles
#     url = (
#         f"https://apis.datos.gob.ar/georef/api/calles?"
#         f"provincia={id_provincia}&localidad_censal={id_localidad_censal}&nombre={calle}&max={max_calles}&aplanar=true"
#     )

#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Lanza un error para respuestas no exitosas
#         calles = response.json().get("calles", [])

#         # Extraemos solo el nombre y la categoría de cada calle
#         calles_filtradas = [
#             {"nombre": calle.get("nombre"), "categoria": calle.get("categoria")}
#             for calle in calles
#         ]

#         return Response({"calles": calles_filtradas}, status=status.HTTP_200_OK)

#     except requests.exceptions.HTTPError as http_err:
#         return Response(
#             {"error": f"Error HTTP: {http_err}"}, status=response.status_code
#         )
#     except requests.exceptions.RequestException as req_err:
#         return Response(
#             {"error": f"Error en la conexión: {req_err}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )
#     except Exception as e:
#         return Response(
#             {"error": f"Error inesperado: {e}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


# @api_view(["POST"])
# @token_required_without_user
# @transaction.atomic
# def crear_direccion(request):
#     try:
#         # Datos de la petición
#         calle = request.POST.get("calle")
#         numero = request.POST.get("numero")
#         contacto = request.POST.get("contacto")
#         email = request.POST.get("email")
#         codigo_postal = request.POST.get("codigo_postal")
#         id_ciudad = request.POST.get("id_ciudad")
#         id_provincia = request.POST.get("id_provincia")

#         if not all([calle, numero, email, codigo_postal, id_ciudad, id_provincia]):
#             return JsonResponse({"error": "Faltan datos obligatorios."}, status=status.HTTP_400_BAD_REQUEST)

#         # Crear o obtener la Direccion
#         direccion = obtener_o_crear_direccion(
#             calle, numero, contacto, email, codigo_postal, id_ciudad, id_provincia
#         )

#         return JsonResponse(
#             {
#                 "mensaje": "Direccion creada exitosamente",
#                 "direccion": {
#                     "calle": direccion.calle,
#                     "numero": direccion.numero,
#                     "contacto": str(direccion.contacto),
#                     "email": direccion.email,
#                     "codigo_postal": direccion.codigo_postal,
#                     "ciudad": direccion.ciudad.nombre,
#                     "provincia": direccion.ciudad.provincia.nombre,
#                     "id_direccion": direccion.idDireccion
#                 },
#             },
#             status=status.HTTP_201_CREATED,
#         )

#     except EntityNotFoundError as e:
#         return JsonResponse({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return JsonResponse({"error": "Ocurrió un error inesperado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(["GET"])
# @token_required_without_user
# def listar_direccion_por_compra(request, idCompra):
#     try:
#         compra = get_object_or_404(Compra, idCompra=idCompra)

#         direccion_data = DireccionSerializer(compra.direccion).data

#         return Response({"direccion": direccion_data}, status=status.HTTP_200_OK)

#     except Exception as e:
#         return JsonResponse(
#             {"error": "Error interno del servidor", "detalle": str(e)},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )

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
        codigo_postal = data["google"]["codigo_postal"]
        contacto = data.get("contacto")  # Puede ser opcional
        email = data.get("email")  # Puede ser opcional
        lat = data["google"]["lat"]
        lon = data["google"]["lon"]

        # Extraer nombres de ciudad y provincia desde Google Maps
        nombre_provincia = data["google"]["provincia"]["nombre"]
        nombre_ciudad = data["google"]["ciudad"]["nombre"]

        with transaction.atomic():
            provincia = Provincia.objects.get(nombre=nombre_provincia)

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


# def guardar_direccion(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)

#             # Extraer datos de Google Maps
#             calle = data["google"]["calle"]
#             numero = data["google"]["numero"]
#             codigo_postal = data["google"]["codigo_postal"]
#             contacto = data.get("contacto")  # Puede ser opcional
#             email = data.get("email")  # Puede ser opcional
#             lat = data["google"]["lat"]
#             lon = data["google"]["lon"]

#             # Extraer nombres de ciudad y provincia desde Google Maps
#             nombre_provincia = data["google"]["provincia"]["nombre"]
#             nombre_ciudad = data["google"]["ciudad"]["nombre"]

#             with transaction.atomic():
#                 provincia, _ = Provincia.objects.get_or_create(nombre=nombre_provincia)
#                 ciudad, _ = Ciudad.objects.get_or_create(
#                     nombre=nombre_ciudad, provincia=provincia
#                 )
#                 coordenada = Coordenada.objects.create(latitud=lat, longitud=lon)
#                 direccion = Direccion.objects.create(
#                     calle=calle,
#                     numero=numero,
#                     codigo_postal=codigo_postal,
#                     contacto=contacto,
#                     email=email,
#                     coordenada=coordenada,
#                     ciudad=ciudad,
#                 )

#             return JsonResponse(
#                 {
#                     "message": "Dirección guardada correctamente",
#                     "id_direccion": direccion.idDireccion,
#                 },
#                 status=201,
#             )

#         except KeyError as e:
#             return JsonResponse({"error": f"Falta el campo requerido: {e}"}, status=400)
#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Error en el formato JSON"}, status=400)
#         except Exception as e:
#             return JsonResponse({"error": f"Error inesperado: {str(e)}"}, status=500)

#     return JsonResponse({"error": "Método no permitido"}, status=405)


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
