import json
from django.test import TestCase
from django.urls import reverse
from phonenumbers import parse, is_valid_number
from .models import Ciudad, Dirección, Provincia  # Asegúrate de que el nombre sea correcto


class CrearDireccionViewTests(TestCase):
    def setUp(self):
        # Configura una ciudad válida para las pruebas
        self.provincia = Provincia.objects.create(nombre="Entre Ríos", idProvincia=30)
        self.ciudad = Ciudad.objects.create(idCiudad = 3000809003,
            nombre="San José", provincia= self.provincia  # Ajusta según tus provincias válidas
        )

    def test_crear_direccion_exitosamente(self):
        response = self.client.post(
            reverse("crear_direccion"),
            {
                "calle": "Calle Falsa",
                "numero": "123",
                "contacto": "5491123456789",
                "email": "test@example.com",
                "codigo_postal": "1234",
                "id_ciudad": self.ciudad.idCiudad,
                "id_provincia": self.provincia.idProvincia,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertJSONEqual(
            response.content,
            {
                "mensaje": "Dirección creada exitosamente",
                "direccion": {
                    "calle": "Calle Falsa",
                    "numero": "123",
                    "contacto": "+5491123456789",  # Verifica el formato esperado
                    "email": "test@example.com",
                    "codigo_postal": "1234",
                    "ciudad": self.ciudad.nombre,
                    "provincia": self.provincia.nombre,  # Cambia según tu modelo
                },
            },
        )

    def test_faltan_datos_obligatorios(self):
        response = self.client.post(
            reverse("crear_direccion"),
            {
                "calle": "",
                "numero": "123",
                "contacto": str(parse("+5491123456789", "AR")),
                "email": "",
                "codigo_postal": "1234",
                "id_ciudad": self.ciudad.idCiudad,
                "id_provincia": self.provincia.idProvincia,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Faltan datos obligatorios."})

    def test_ciudad_no_existente(self):
        response = self.client.post(
            reverse("crear_direccion"),
            {
                "calle": "Calle Falsa",
                "numero": "123",
                "contacto": str(parse("+5491123456789", "AR")),
                "email": "test@example.com",
                "codigo_postal": "1234",
                "id_ciudad": 9999,  # ID que no existe
                "id_provincia": self.provincia.idProvincia,
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(
            response.content,
            {
                "error": "La ciudad con ID 9999 no existe en la API de Georef."
            },  # Asegúrate de que tu vista maneje este error
        )
