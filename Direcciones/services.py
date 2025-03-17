import requests
from .models import Coordenada, Provincia, Departamento, Municipio, Direccion
from django.conf import settings

GEOREF_URL = "https://apis.datos.gob.ar/georef/api/ubicacion"
GOOGLE_MAPS_API_KEY = settings.GOOGLE_MAPS_API_KEY

def obtener_info_georef(lat, lon):
    """Consulta la API de Georef Argentina y devuelve la ubicación."""
    params = {"lat": lat, "lon": lon}
    response = requests.get(GEOREF_URL, params=params)
    if response.status_code == 200:
        return response.json().get("ubicacion", {})
    return None

import requests


def obtener_info_google_maps(lat, lon):
    """Consulta la API de Google Maps y devuelve número de calle, calle, ciudad, provincia y código postal."""
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "OK":
            address_components = data["results"][0]["address_components"]

            # Diccionario para almacenar los valores
            direccion = {
                "numero": None,
                "calle": None,
                "ciudad": None,
                "provincia": None,
                "cp": None,
            }

            for component in address_components:
                if "street_number" in component["types"]:
                    direccion["numero"] = component["long_name"]
                if "route" in component["types"]:
                    direccion["calle"] = component["long_name"]
                if "locality" in component["types"]:
                    direccion["ciudad"] = component["long_name"]
                if "administrative_area_level_1" in component["types"]:
                    direccion["provincia"] = component["long_name"]
                if "postal_code" in component["types"]:
                    direccion["cp"] = component["long_name"]

            return direccion

    return None
