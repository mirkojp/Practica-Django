import requests
from django.db import transaction
from .models import Provincia, Ciudad, Dirección
from .exceptions import EntityNotFoundError

import requests
from .exceptions import EntityNotFoundError
from .models import Provincia, Ciudad, Dirección


def obtener_o_crear_provincia(id_provincia):
    """
    Intenta obtener una provincia de la base de datos por su ID.
    Si no existe, consulta la API de Georef Argentina para obtener
    la provincia y la crea en la base de datos.

    Args:
        id_provincia (int): El ID de la provincia a obtener o crear.

    Returns:
        Provincia: La instancia de la provincia obtenida o creada.

    Raises:
        EntityNotFoundError: Si la provincia no existe en la base de datos
                             ni en la API de Georef.
    """
    try:
        return Provincia.objects.get(idProvincia=id_provincia)
    except Provincia.DoesNotExist:
        # Si no existe, consultar la API de Georef Argentina
        url = f"https://apis.datos.gob.ar/georef/api/provincias?id={id_provincia}&max=1"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            provincias = data.get("provincias", [])

            if provincias:
                # Extraer la primera provincia de la lista
                provincia_data = provincias[0]
                nombre_provincia = provincia_data.get("nombre")
                api_id = provincia_data.get(
                    "id"
                )  # Obtener el id proporcionado por la API

                # Crear la provincia en la base de datos con la ID de la API
                provincia = Provincia(idProvincia=api_id, nombre=nombre_provincia)
                provincia.save()
                return provincia
            else:
                raise EntityNotFoundError(
                    f"No se encontró una provincia con ID {id_provincia}."
                )
        else:
            raise EntityNotFoundError(
                f"La provincia con ID {id_provincia} no existe en la API de Georef."
            )


def obtener_o_crear_ciudad(id_ciudad, id_provincia):
    """
    Intenta obtener una ciudad de la base de datos por su ID y el ID de su provincia.
    Si no existe, consulta la API de Georef Argentina para obtener
    la ciudad y la crea en la base de datos.

    Args:
        id_ciudad (int): El ID de la ciudad a obtener o crear.
        id_provincia (int): El ID de la provincia a la que pertenece la ciudad.

    Returns:
        Ciudad: La instancia de la ciudad obtenida o creada.

    Raises:
        EntityNotFoundError: Si la ciudad no existe en la base de datos
                             ni en la API de Georef.
    """
    try:
        return Ciudad.objects.get(idCiudad=id_ciudad, provincia_id=id_provincia)
    except Ciudad.DoesNotExist:
        # Si no existe, consultar la API de Georef Argentina
        url = f"https://apis.datos.gob.ar/georef/api/localidades?id={id_ciudad}&max=1"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            ciudades = data.get("localidades", [])

            if ciudades:
                # Extraer la primera ciudad de la lista
                ciudad_data = ciudades[0]
                nombre_ciudad = ciudad_data.get("nombre")
                api_id = ciudad_data.get("id")  # Obtener el id proporcionado por la API

                # Asegúrate de que la provincia existe
                provincia = obtener_o_crear_provincia(id_provincia)

                # Crear la ciudad en la base de datos con la ID de la API
                ciudad = Ciudad(
                    idCiudad=api_id, nombre=nombre_ciudad, provincia=provincia
                )
                ciudad.save()
                return ciudad
            else:
                raise EntityNotFoundError(
                    f"No se encontró una ciudad con ID {id_ciudad}."
                )
        else:
            raise EntityNotFoundError(
                f"La ciudad con ID {id_ciudad} no existe en la API de Georef."
            )


def obtener_o_crear_direccion(
    calle, numero, contacto, email, codigo_postal, id_ciudad, id_provincia
):
    """
    Intenta obtener una dirección de la base de datos por su calle y número.
    Si no existe, crea la dirección en la base de datos, asegurándose
    de que la ciudad y la provincia correspondientes existan.

    Args:
        calle (str): La calle de la dirección.
        numero (int): El número de la dirección.
        contacto (str): El número de contacto.
        email (str): La dirección de correo electrónico.
        codigo_postal (str): El código postal de la dirección.
        id_ciudad (int): El ID de la ciudad donde se encuentra la dirección.
        id_provincia (int): El ID de la provincia donde se encuentra la ciudad.

    Returns:
        Dirección: La instancia de la dirección obtenida o creada.
    """
    try:
        return Dirección.objects.get(calle=calle, numero=numero, ciudad_id=id_ciudad)
    except Dirección.DoesNotExist:
        # Si no existe, crear la dirección en la base de datos
        ciudad = obtener_o_crear_ciudad(id_ciudad, id_provincia)
        direccion = Dirección(
            calle=calle,
            numero=numero,
            contacto=contacto,
            email=email,
            codigo_postal=codigo_postal,
            ciudad=ciudad,
        )
        direccion.save()
        return direccion
