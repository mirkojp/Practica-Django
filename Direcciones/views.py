from rest_framework import viewsets
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import DirecciónSerializer
from .models import Dirección

def obtener_provincias(request):
    """
    Obtiene la lista de provincias desde la API de Georef.

    Ejemplo de uso:
    GET http://localhost:8000/obtener_provincias
    """
    url = "https://apis.datos.gob.ar/georef/api/provincias"

    try:
        response = requests.get(url)
        response.raise_for_status()  

        if "provincias" in response.json():
            return Response(response.json()["provincias"], status=200)
        else:
            return Response({"error": "No se encontraron provincias en la respuesta."}, status=404)

    except requests.exceptions.HTTPError as http_err:
        return Response(
            {"error": f"Error HTTP: {http_err}"}, status=response.status_code
        )
    except requests.exceptions.RequestException as req_err:
        return Response({"error": f"Error en la conexión: {req_err}"}, status=500)
    except Exception as e:
        return Response({"error": f"Error inesperado: {e}"}, status=500)


# @api_view(["GET"])
# def localidades_por_provincia(request, id_provincia):
#     url = f"https://apis.datos.gob.ar/georef/api/localidades?provincia={id_provincia}"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()

#         localidades = response.json().get("localidades", [])

#         return Response({"localidades": localidades}, status=200)

#     except Exception as e:
#         return Response({"error": f"Error inesperado: {e}"}, status=500)


@api_view(["GET"])
def localidades_por_provincia(request, id_provincia):
    """
    Obtiene localidades de una provincia específica filtradas por nombre.

    Parámetros de consulta:
    - localidad: Nombre de la localidad a buscar (requerido).
    - max: Límite máximo de localidades a devolver (opcional, predeterminado 100).

    Ejemplo de uso:
    GET http://localhost:8000/localidades/30/?localidad=san&max=100
    """

    localidad = request.query_params.get("localidad", "")
    if not localidad:
        return Response(
            {"error": "El parámetro 'localidad' no puede estar vacío."}, status=400
        )

    # Validar el parámetro max
    max_localidades_str = request.query_params.get("max", 100)
    try:
        max_localidades = int(max_localidades_str)
        if max_localidades <= 0:
            return Response(
                {"error": "'max' debe ser un número entero positivo."}, status=400
            )
    except ValueError:
        return Response({"error": "'max' debe ser un número entero."}, status=400)

    url = (
        f"https://apis.datos.gob.ar/georef/api/localidades?"
        f"provincia={id_provincia}&nombre={localidad}&max={max_localidades}&aplanar=true&campos=basico"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error para respuestas no exitosas
        localidades = response.json().get("localidades", [])

        return Response({"localidades": localidades}, status=200)

    except requests.exceptions.HTTPError as http_err:
        return Response(
            {"error": f"Error HTTP: {http_err}"}, status=response.status_code
        )
    except requests.exceptions.RequestException as req_err:
        return Response({"error": f"Error en la conexión: {req_err}"}, status=500)
    except Exception as e:
        return Response({"error": f"Error inesperado: {e}"}, status=500)


@api_view(["POST"])
def crear_direccion(request):
    """
    Crea una nueva dirección a partir de los datos enviados desde el frontend.
    """
    serializer = DirecciónSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def listar_direccion(request, id):
    """
    Retorna los detalles de una dirección específica.
    """
    try:
        direccion = Dirección.objects.get(idDireccion=id)
        serializer = DirecciónSerializer(direccion)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Dirección.DoesNotExist:
        return Response(
            {"error": "Dirección no encontrada."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
