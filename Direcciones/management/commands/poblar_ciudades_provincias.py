import requests
from django.core.management.base import BaseCommand
from Direcciones.models import Provincia, Ciudad


class Command(BaseCommand):
    help = (
        "Poblar la base de datos con las provincias y ciudades desde la API de Georef"
    )

    def handle(self, *args, **kwargs):
        # Poblar Provincias
        provincias_url = "https://apis.datos.gob.ar/georef/api/provincias"
        response = requests.get(provincias_url)
        if response.status_code == 200:
            provincias_data = response.json().get("provincias", [])
            for provincia in provincias_data:
                Provincia.objects.get_or_create(
                    idProvincia=provincia["id"], nombre=provincia["nombre"]
                )
            self.stdout.write(self.style.SUCCESS("Provincias cargadas correctamente"))
        else:
            self.stdout.write(
                self.style.ERROR(f"Error al obtener provincias: {response.status_code}")
            )

        # Poblar Ciudades
        ciudades_url = "https://apis.datos.gob.ar/georef/api/localidades?campos=id,nombre,provincia"
        response = requests.get(ciudades_url)
        if response.status_code == 200:
            ciudades_data = response.json().get("localidades", [])
            for ciudad in ciudades_data:
                provincia = Provincia.objects.get(idProvincia=ciudad["provincia"]["id"])
                Ciudad.objects.get_or_create(
                    idCiudad=ciudad["id"], nombre=ciudad["nombre"], provincia=provincia
                )
            self.stdout.write(self.style.SUCCESS("Ciudades cargadas correctamente"))
        else:
            self.stdout.write(
                self.style.ERROR(f"Error al obtener ciudades: {response.status_code}")
            )
