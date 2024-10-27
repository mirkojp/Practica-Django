def test_crear_direccion_sin_token(self):
        # Realiza una solicitud POST sin el encabezado de autorización
        response = self.client.post(
            self.url,
            {
                "calle": "Calle Falsa",
                "numero": "123",
                "contacto": "+5491123456789",
                "email": "test@example.com",
                "codigo_postal": "1234",
                "id_ciudad": self.ciudad.idCiudad,
                "id_provincia": self.provincia.idProvincia,
            },
        )
        print(response.data)

        # Verifica que la respuesta sea un error de autenticación (403 Forbidden o 401 Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  # O 401 dependiendo de la configuración de tu API
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')  # 