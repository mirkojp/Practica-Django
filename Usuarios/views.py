from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Token
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import UsuarioSerializer
from .models import Usuario
from Compras.models import Carrito
from django.db import IntegrityError
from django.db import transaction
from Utils.validarcontacto import validar_contacto
from rest_framework.parsers import JSONParser
from google.oauth2 import id_token
from google.auth.transport import requests
import os


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

                # Crear el carrito asociado al usuario recién creado
                carrito = Carrito.objects.create(usuario=usuario)

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


# Configura tu CLIENT_ID aquí (el ID de cliente de tu aplicación de Google)
GOOGLE_CLIENT_ID = os.getenv("455918670543-a7apj0vtfdjc3r2e9g0m0h3mr7dr0q5u.apps.googleusercontent.com")
@api_view(["POST"])
def google(request):
    if request.method == 'POST':
        try:
            # Obtén el token enviado desde el frontend
            token_google = request.data.get('token')

            return JsonResponse({"token" : token_google})

            # Verifica el token de Google
            id_info = id_token.verify_oauth2_token(token_google, requests.Request(), GOOGLE_CLIENT_ID)

            # Extrae la información del usuario del token
            google_user_id = id_info['sub']
            email = id_info.get('email')
            name = id_info.get('name')

            # Verifica si el usuario ya existe
            usuario, created = Usuario.objects.get_or_create(nombre=name, email=email)

            # Crea una sesión o token para el usuario
            if created:
                # Si el usuario fue creado, aquí podrías asignarle una contraseña temporal u otras configuraciones.
                usuario.save()
            
            # Crea o obtiene el token de autenticación
            token, created = Token.objects.get_or_create(user=usuario)

            # Devuelve un token o mensaje de éxito al frontend
            return JsonResponse({
                'success': True,
                'message': 'Usuario autenticado exitosamente.',
                'user_id': usuario.idUsuario,
                "token" : token
            })

        except ValueError:
            # El token no es válido
            return JsonResponse({'error': 'Token de Google no válido'}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@api_view(['GET', 'PUT', 'DELETE'])
def listar_usuario(request, id):    #Resuelve /usuarios/{id}

    if request.method == 'GET':
        # Obtener el token del encabezado de la solicitud
        token = request.headers.get('Authorization')

        if not token or not token.startswith('Token '):
            return Response({"error": "Token no provisto o incorrecto."}, status=status.HTTP_401_UNAUTHORIZED)

        # Extraer el token después de la palabra 'Token '
        token_key = token.split(' ')[1]

        try:
            # Buscar el token en la base de datos
            token = Token.objects.get(key=token_key)
            usuario = token.user  # Obtener el usuario asociado al token
            serializer = UsuarioSerializer(instance=usuario)

            # Verificar que el usuario tiene acceso solo a sus propios datos
            if usuario.idUsuario != id and not usuario.is_staff:  # Sólo el usuario o un administrador pueden ver los datos
                return Response({"error": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

            # Si todo está correcto, devuelve los datos del usuario
            return Response(
                {
                    "Usuario": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Token.DoesNotExist:
            return Response({"error": "Token inválido o no encontrado."}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    elif request.method == 'PUT':
        # Obtener el token del encabezado de la solicitud
        token = request.headers.get('Authorization')

        if not token or not token.startswith('Token '):
            return Response({"error": "Token no provisto o incorrecto."}, status=status.HTTP_401_UNAUTHORIZED)

        # Extraer el token después de la palabra 'Token '
        token_key = token.split(' ')[1]
        
        try:
            # Buscar el token en la base de datos
            token = Token.objects.get(key=token_key)
            usuario = token.user  # Obtener el usuario asociado al token

            # Verificar que el usuario tiene acceso solo a sus propios datos
            if usuario.idUsuario != id:  # Sólo el usuario puede modificar los datos
                return Response({"error": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

            # Actualizar los datos del usuario
            data = JSONParser().parse(request)
            for key, value in data.items():
                if hasattr(usuario, key):  # Asegurarse de que el campo existe en el modelo de Usuario
                    if key != "email":
                        if key != "password":
                            setattr(usuario, key, value)
                        else:
                            usuario.set_password(value)
                    else:
                        if value != usuario.email:
                            setattr(usuario, key, value)

            # Guardar los cambios
            usuario.save()
            serializer = UsuarioSerializer(instance=usuario)

            return Response(
                {
                    "Usuario": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Token.DoesNotExist:
            return Response({"error": "Token inválido o no encontrado."}, status=status.HTTP_401_UNAUTHORIZED)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    elif request.method == 'DELETE':
        # Obtener el token del encabezado de la solicitud
        token = request.headers.get('Authorization')

        if not token or not token.startswith('Token '):
            return Response({"error": "Token no provisto o incorrecto."}, status=status.HTTP_401_UNAUTHORIZED)

        # Extraer el token después de la palabra 'Token '
        token_key = token.split(' ')[1]

        try:
            # Buscar el token en la base de datos
            token = Token.objects.get(key=token_key)
            usuario = token.user  # Obtener el usuario asociado al token

            # Verificar que el usuario tiene acceso solo a sus propios datos
            if usuario.idUsuario != id:  # Sólo el usuario puede borrar los datos
                return Response({"error": "No autorizado."}, status=status.HTTP_401_UNAUTHORIZED)

            # Elimina el carrito asociado al usuario
            Carrito.objects.filter(usuario=usuario).exists() and Carrito.objects.filter(usuario=usuario).delete()

            #Borra el usuario de la bse de datos
            usuario.delete()

            return Response(status=status.HTTP_200_OK)

        except Token.DoesNotExist:
            return Response({"error": "Token inválido o no encontrado."}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)