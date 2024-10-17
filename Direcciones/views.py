from rest_framework import viewsets
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import DirecciónSerializer
from .models import Dirección


@api_view(["GET"])
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
            return Response(response.json()["provincias"], status=status.HTTP_200_OK)
        else:
            return Response({"error": "No se encontraron provincias en la respuesta."}, status=status.HTTP_404_NOT_FOUND)

    except requests.exceptions.HTTPError as http_err:
        return Response(
            {"error": f"Error HTTP: {http_err}"}, status=response.status_code
        )
    except requests.exceptions.RequestException as req_err:
        return Response({"error": f"Error en la conexión: {req_err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response(
            {"error": f"Error inesperado: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


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
            {"error": "El parámetro 'localidad' no puede estar vacío."}, status=status.HTTP_400_BAD_REQUEST
        )

    # Validar el parámetro max
    max_localidades_str = request.query_params.get("max", 100)
    try:
        max_localidades = int(max_localidades_str)
        if max_localidades <= 0:
            return Response(
                {"error": "'max' debe ser un número entero positivo."}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({"error": "'max' debe ser un número entero."}, status=status.HTTP_400_BAD_REQUEST)

    url = (
        f"https://apis.datos.gob.ar/georef/api/localidades?"
        f"provincia={id_provincia}&nombre={localidad}&max={max_localidades}&aplanar=true&campos=basico"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error para respuestas no exitosas
        localidades = response.json().get("localidades", [])

        return Response({"localidades": localidades}, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as http_err:
        return Response(
            {"error": f"Error HTTP: {http_err}"}, status=response.status_code
        )
    except requests.exceptions.RequestException as req_err:
        return Response({"error": f"Error en la conexión: {req_err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response(
            {"error": f"Error inesperado: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )



@api_view(["GET"])
def localidades_censales_por_provincia(request, id_provincia):
    """
    Obtiene localidades censales de una provincia específica filtradas por nombre.

    Parámetros de consulta:
    - localidad: Nombre de la localidad censal a buscar (requerido).
    - max: Límite máximo de localidades censales a devolver (opcional, predeterminado 100).

    Ejemplo de uso:
    GET http://localhost:8000/localidades-censales/30/?localidad=san&max=100
    """

    localidad = request.query_params.get("localidad", "")
    if not localidad:
        return Response(
            {"error": "El parámetro 'localidad' no puede estar vacío."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validar el parámetro max
    max_localidades_str = request.query_params.get("max", 100)
    try:
        max_localidades = int(max_localidades_str)
        if max_localidades <= 0:
            return Response(
                {"error": "'max' debe ser un número entero positivo."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except ValueError:
        return Response(
            {"error": "'max' debe ser un número entero."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Cambiamos la URL para consultar localidades censales en lugar de localidades normales
    url = (
        f"https://apis.datos.gob.ar/georef/api/localidades-censales?"
        f"provincia={id_provincia}&nombre={localidad}&max={max_localidades}&aplanar=true&campos=basico"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error para respuestas no exitosas
        localidades_censales = response.json().get("localidades_censales", [])

        return Response(
            {"localidades_censales": localidades_censales}, status=status.HTTP_200_OK
        )

    except requests.exceptions.HTTPError as http_err:
        return Response(
            {"error": f"Error HTTP: {http_err}"}, status=response.status_code
        )
    except requests.exceptions.RequestException as req_err:
        return Response(
            {"error": f"Error en la conexión: {req_err}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        return Response(
            {"error": f"Error inesperado: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def calles_por_localidad_censal(request, id_provincia, id_localidad_censal):
    """
    Obtiene calles de una localidad censal específica filtradas por nombre.

    Parámetros de consulta:
    - calle: Nombre de la calle a buscar (requerido).
    - max: Límite máximo de calles a devolver (opcional, predeterminado 100).

    Ejemplo de uso:
    GET http://localhost:8000/calles/30/30088020/?calle=paoloni&max=100
    """

    calle = request.query_params.get("calle", "")
    if not calle:
        return Response(
            {"error": "El parámetro 'calle' no puede estar vacío."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validar el parámetro max
    max_calles_str = request.query_params.get("max", 100)
    try:
        max_calles = int(max_calles_str)
        if max_calles <= 0:
            return Response(
                {"error": "'max' debe ser un número entero positivo."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except ValueError:
        return Response(
            {"error": "'max' debe ser un número entero."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Construimos la URL para consultar las calles
    url = (
        f"https://apis.datos.gob.ar/georef/api/calles?"
        f"provincia={id_provincia}&localidad_censal={id_localidad_censal}&nombre={calle}&max={max_calles}&aplanar=true"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error para respuestas no exitosas
        calles = response.json().get("calles", [])

        # Extraemos solo el nombre y la categoría de cada calle
        calles_filtradas = [
            {"nombre": calle.get("nombre"), "categoria": calle.get("categoria")}
            for calle in calles
        ]

        return Response({"calles": calles_filtradas}, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as http_err:
        return Response(
            {"error": f"Error HTTP: {http_err}"}, status=response.status_code
        )
    except requests.exceptions.RequestException as req_err:
        return Response(
            {"error": f"Error en la conexión: {req_err}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        return Response(
            {"error": f"Error inesperado: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


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


@api_view(["DELETE"])
def eliminar_direccion(request, id):
    """
    Elimina una dirección existente.
    """
    try:
        direccion = Dirección.objects.get(idDireccion=id)
        direccion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Dirección.DoesNotExist:
        return Response(
            {"error": "Dirección no encontrada."}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def actualizar_direccion(request, id):
    """"
    Al actualizar una direccion debe primero evaluarse si existen compras,
    con esa direccion, de ser asi debe crearse una direccion nueva persistiendo la anterior
    en caso contrario se elimina la direccion
    """
    #todo
