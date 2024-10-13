from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Token
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import UsuarioSerializer
from .models import Usuario
from django.db import IntegrityError
from django.db import transaction

# Create your views here.

@api_view(["POST"]) #Resuelve /usuarios/login
def login(request):

    try:
        #Busca el usuario con el nombre ingresado
        usuario = get_object_or_404(Usuario, nombre=request.data["nombre"])

        #Si no coinside la password retorno el mensaje y status
        if not usuario.check_password(request.data["password"]):
            return Response(
                {
                    "Mensaje": "Credenciales incorrectas"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crea o obtiene el token de autenticación
        token, created = Token.objects.get_or_create(user=usuario)
        serializer = UsuarioSerializer(instance=usuario)

        return Response(
            {
                "Mensaje": "Inicio de sesion exitoso",
                "Token": token.key,
                "Usuario": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    except KeyError: #Excepcion que controla los parametros de autenticacion necesarios
        return Response("Falta parametos de autenticacion", status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(["POST"])  #Resuelve /usuarios
def register(request):
    #Verifica que la request tenga todos los datos necesarios
    serializer = UsuarioSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                # Crear el usuario utilizando el método save del serializer
                serializer.save()

                # Asignar la contraseña
                usuario = Usuario.objects.get(nombre=serializer.data["nombre"])
                usuario.set_password(serializer.validated_data["password"])
                usuario.save()  # Guardar el usuario con la contraseña encriptada


                # Crear el token de autenticación
                token = Token.objects.create(user=usuario)

            return Response(
                {
                    "Mensaje": "Recurso creado exitosamente",
                    "Token": token.key,
                    "Usuario": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except IntegrityError:
            # Manejo de excepciones si hay un error de integridad
            return Response({"error": "Ya existe un usuario con ese email."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Manejo de otras excepciones
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    