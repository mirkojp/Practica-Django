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

def obtener_info_google_maps(lat, lon):
    """Consulta la API de Google Maps y devuelve la dirección."""
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("results", [])
    return None
