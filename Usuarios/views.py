from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Token, Reseña
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import UsuarioSerializer, ReseñaSerializer
from .models import Usuario
from Compras.models import Carrito, CarritoItem, Compra
from Compras.serializers import CarritoItemSerializer, CompraSerializer
from django.db import IntegrityError
from django.db import transaction
from Utils.validarcontacto import validar_contacto
from rest_framework.parsers import JSONParser
from google.oauth2 import id_token
from google.auth.transport import requests
import os
import requests as requestf
from requests_oauthlib import OAuth1Session
from django.shortcuts import redirect
from Utils.tokenAuthorization import userAuthorization, adminAuthorization
from Productos.models import Funko
from Productos.serializers import FunkoSerializer


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


@api_view(["POST", "GET"])  #Resuelve /usuarios
def register(request):

    if request.method == "POST":
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
        
    elif request.method == "GET":

        # Llama a userAuthorization para verificar el token y obtener el usuario
        usuario, error_response = adminAuthorization(request)

        if error_response: # Retorna el error si el token es inválido o no encontrado
            return error_response
        
        try:
            # Obtener todos los usuarios
            usuarios = Usuario.objects.all()
            usuarios_serializer = UsuarioSerializer(usuarios, many=True)

            return Response(
                {"usuarios": usuarios_serializer.data}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Configura tu CLIENT_ID aquí (el ID de cliente de tu aplicación de Google)
GOOGLE_CLIENT_ID = os.getenv("455918670543-a7apj0vtfdjc3r2e9g0m0h3mr7dr0q5u.apps.googleusercontent.com")
@api_view(["POST"])
def register_google(request):
    if request.method == 'POST':
        try:
            # Obtén el token enviado desde el frontend
            token_google = request.data.get('token')

            
            # Verifica el token de Google
            id_info = id_token.verify_oauth2_token(token_google, requests.Request(), GOOGLE_CLIENT_ID)

            # Extrae la información del usuario del token
            email = id_info["email"]
            name = id_info["name"]

            # Verifica si el usuario ya existe
            usuario = Usuario.objects.filter(email=email)

            # Crea una sesión o token para el usuario
            if usuario:
                return Response({"error" : "Ya existe una cuenta registrada con esas credenciales"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                usuario = Usuario.objects.create(email=email, nombre=name)
                usuario.save()
            
            # Crea o obtiene el token de autenticación
            token = Token.objects.create(user=usuario)
            serializer = UsuarioSerializer(instance=usuario)

            # Crear el carrito asociado al usuario recién creado
            carrito = Carrito.objects.create(usuario=usuario)
            

            # Devuelve un token o mensaje de éxito al frontend
            return Response({
                'success': True,
                'message': 'Usuario autenticado exitosamente.',
                'usuario': serializer.data,
                "token" : token.key
            })
        except Exception as e:
            # Manejo de otras excepciones
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def login_google(request):
    if request.method == 'POST':
        try:
            # Obtén el token enviado desde el frontend
            token_google = request.data.get('token')

            # Verifica el token de Google
            id_info = id_token.verify_oauth2_token(token_google, requests.Request(), GOOGLE_CLIENT_ID)

            # Extrae la información del usuario del token
            email = id_info["email"]
            name = id_info["name"]

            # Verifica si el usuario ya existe
            usuario = Usuario.objects.get(email=email, nombre=name)

            
            # Crea o obtiene el token de autenticación
            token = Token.objects.get(user=usuario)
            serializer = UsuarioSerializer(instance=usuario)
            

            # Devuelve un token o mensaje de éxito al frontend
            return Response({
                'success': True,
                'message': 'Usuario autenticado exitosamente.',
                'usuario': serializer.data,
                "token" : token.key
            })
        except Usuario.DoesNotExist:
            return Response({"error" : "Debe registrarse primero."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            # Manejo de otras excepciones
            return Response({"error": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def register_facebook(request):
    if request.method == 'POST':
        try:
            # Definir client_id y client_secret directamente en la vista
            FACEBOOK_CLIENT_ID = '1205840470714772'
            FACEBOOK_CLIENT_SECRET = '987184f52149730f290e7d376c15c4ef'

            # Recibe el token enviado desde el frontend
            access_token = request.data['token']

            # Llama al endpoint de Facebook para obtener los datos del usuario
            user_info_url = "https://graph.facebook.com/me"
            params = {
                'access_token': access_token,
                'fields': 'id,name,email,picture'
            }

            # Realiza la solicitud a la API de Facebook
            response = requestf.get(user_info_url, params=params)
            response_data = response.json()
            
            # Si hubo un error con la solicitud a Facebook
            if 'error' in response_data:
                return Response({'error': response_data['error']['message']}, status=400)
            
            # Extrae los datos del usuario
            name = response_data.get('name')
            email = response_data.get('email')

            # Verifica si el usuario ya existe
            usuario = Usuario.objects.filter(email=email)

            # Crea una sesión o token para el usuario
            if usuario:
                return Response({"error" : "Ya existe una cuenta registrada con esas credenciales"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                usuario = Usuario.objects.create(email=email, nombre=name)
                usuario.save()
            
            # Crea o obtiene el token de autenticación
            token = Token.objects.create(user=usuario)
            serializer = UsuarioSerializer(instance=usuario)

            # Devuelve un token o mensaje de éxito al frontend
            return Response({
                'success': True,
                'message': 'Usuario autenticado exitosamente.',
                'usuario': serializer.data,
                "token" : token.key
            })
        except Exception as e:
            # Manejo de otras excepciones
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def login_facebook(request):
    if request.method == 'POST':
        try:
            # Definir client_id y client_secret directamente en la vista
            FACEBOOK_CLIENT_ID = '1205840470714772'
            FACEBOOK_CLIENT_SECRET = '987184f52149730f290e7d376c15c4ef'

            # Recibe el token enviado desde el frontend
            access_token = request.data['token']

            # Llama al endpoint de Facebook para obtener los datos del usuario
            user_info_url = "https://graph.facebook.com/me"
            params = {
                'access_token': access_token,
                'fields': 'id,name,email,picture'
            }

            # Realiza la solicitud a la API de Facebook
            response = requestf.get(user_info_url, params=params)
            response_data = response.json()

            # Si hubo un error con la solicitud a Facebook
            if 'error' in response_data:
                return Response({'error': response_data['error']['message']}, status=400)

            # Extrae los datos del usuario
            name = response_data.get('name')
            email = response_data.get('email')

            # Verifica si el usuario ya existe
            usuario = Usuario.objects.get(email=email, nombre=name)

            # Crea o obtiene el token de autenticación
            token = Token.objects.get(user=usuario)
            serializer = UsuarioSerializer(instance=usuario)

            # Devuelve un token o mensaje de éxito al frontend
            return Response({
                'success': True,
                'message': 'Usuario autenticado exitosamente.',
                'usuario': serializer.data,
                "token" : token.key
            })
        except Usuario.DoesNotExist:
            return Response({"error" : "Debe registrarse primero."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Manejo de otras excepciones
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#consumerKey = "zvuyvz3or8uMwzGGugpcl2f2Q"
#consumerSecret = "ZYbD70FPfubZcwvKMrggprs1Uk9MBfLPPu4x5IQ1PYUZzAsCdK"
consumerKey = "jtiMOwxO7zvnACaPDuAmy9mB1"
consumerSecret = "nqGa1pPVQp0Rh4aaYGGLQr4JNzIAUzv5iwaQIfXbFDqkoIbpet"
# Vista para iniciar la autenticación
@api_view(['GET'])
def twitter_login(request):
    twitter = OAuth1Session(consumerKey, consumerSecret)
    request_token_url = "https://api.twitter.com/oauth/request_token"
    
    try:
        # Obtén el request token de Twitter
        fetch_response = twitter.fetch_request_token(request_token_url)
        oauth_token = fetch_response.get('oauth_token')
        oauth_token_secret = fetch_response.get('oauth_token_secret')
        
        # Crea la URL de autorización incluyendo el oauth_token
        authorization_url = twitter.authorization_url("https://api.twitter.com/oauth/authorize", oauth_token=oauth_token)
        
        # Devuelve la URL de autorización al frontend
        return Response({"authorization_url": authorization_url}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Vista de callback que Twitter redirige con oauth_token y oauth_verifier
@api_view(['POST'])
def twitter_callback(request):
    oauth_token = request.data.get('oauth_token')
    oauth_verifier = request.data.get('oauth_verifier')

    if not oauth_token or not oauth_verifier:
        return Response({"error": "Faltan parámetros para la autenticación"}, status=status.HTTP_400_BAD_REQUEST)

    # Crea una nueva sesión OAuth con el request token
    twitter = OAuth1Session(
        consumerKey,
        consumerSecret,
        resource_owner_key=oauth_token,
        verifier=oauth_verifier
    )

    # Intercambia oauth_token y oauth_verifier por el Access Token
    access_token_url = "https://api.twitter.com/oauth/access_token"
    try:
        oauth_tokens = twitter.fetch_access_token(access_token_url)
        access_token = oauth_tokens.get('oauth_token')
        access_token_secret = oauth_tokens.get('oauth_token_secret')

        # Aquí puedes usar el access_token y access_token_secret para acceder a datos del usuario
        # Suponemos que obtienes 'email' y 'name' del usuario (aunque Twitter no siempre proporciona email)
        user_info_url = "https://api.twitter.com/1.1/account/verify_credentials.json?include_email=true"
        twitter = OAuth1Session(
            consumerKey,
            consumerSecret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )
        user_info = twitter.get(user_info_url).json()

        # Procesa la información del usuario
        email = user_info.get("email")
        name = user_info.get("name")

        # Verifica si el usuario ya existe
        usuario = Usuario.objects.filter(email=email)

        # Crea una sesión o token para el usuario
        if usuario:
            if not usuario.nombre == name:
                return Response({"error" : "Ya existe una cuenta registrada con esas credenciales"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            usuario = Usuario.objects.create(email=email, nombre=name)
            usuario.save()
            
        # Crea o obtiene el token de autenticación
        token = Token.objects.create(user=usuario)
        serializer = UsuarioSerializer(instance=usuario)

        # Crear el carrito asociado al usuario recién creado
        carrito = Carrito.objects.create(usuario=usuario)
        
        return Response({
            'success': True,
            'message': 'Usuario autenticado exitosamente.',
            'usuario': serializer.data,
            "token" : token.key,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def github_login(request):
    # Redirige al usuario a la URL de autorización de GitHub
    github_auth_url = "https://github.com/login/oauth/authorize"
    redirect_uri = "https://practica-django-fxpz.onrender.com/auth/github/callback/"
    url = f"{github_auth_url}?client_id=Ov23liqrSR5ByM2QzZKw&redirect_uri={redirect_uri}&scope=user"
    return Response({"url": url}, status=status.HTTP_200_OK)
    # return redirect(url)

@api_view(['GET'])
def github_callback(request):

    try:
        # Obtiene el `code` que GitHub envía a esta vista como parte del flujo de autorización
        code = request.GET.get('code')

        if not code:
            return Response({"error": "Authorization failed, code missing"}, status=status.HTTP_400_BAD_REQUEST)

        # Intercambia el código de autorización por un access token
        token_url = "https://github.com/login/oauth/access_token"
        data = {
            "client_id": "Ov23liqrSR5ByM2QzZKw",
            "client_secret": "bec8349901eb904f4b1671b0c082582404c8dbf6",
            "code": code,
        }
        headers = {'Accept': 'application/json'}
        token_response = requestf.post(token_url, data=data, headers=headers)
        token_json = token_response.json()
        access_token = token_json.get("access_token")

        if not access_token:
            return Response({"error": "Failed to retrieve access token"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Usa el access token para obtener los datos del usuario
        user_info_url = "https://api.github.com/user"
        headers = {'Authorization': f'token {access_token}'}
        user_info_response = requestf.get(user_info_url, headers=headers)
        user_data = user_info_response.json()

        # Aquí puedes crear o verificar el usuario en tu base de datos
        # Ejemplo de guardar email y nombre en la BD (puede variar según tu modelo)
        name = user_data["login"]

        email_url = "https://api.github.com/user/emails"
        headers = {'Authorization': f'token {access_token}'}
        email_response = requestf.get(email_url, headers=headers)
        emails = email_response.json()

        # Encuentra el email principal o público del usuario
        primary_email = next((email['email'] for email in emails if email['primary']), None)

        if primary_email and name:
            # Guardar o autenticar el usuario en la BD
            # Devuelve el token de autenticación al frontend

            # Verifica si el usuario ya existe
            usuario = Usuario.objects.filter(email=primary_email).first()

            # Crea una sesión o token para el usuario
            if usuario:
                if not usuario.nombre == name:
                    url = f'https://importfunkologin.netlify.app/?errorIntegridad=""'
                    return redirect(url)
            else:
                usuario = Usuario.objects.create(email=primary_email, nombre=name)
                usuario.save()

            # Crea o obtiene el token de autenticación
            token, created = Token.objects.get_or_create(user=usuario)

            # Crear el carrito asociado al usuario recién creado
            carrito = Carrito.objects.create(usuario=usuario)

            # Redirige al frontend con los datos en la URL (solo para pruebas; en producción, usa un almacenamiento seguro)
            frontend_url = f"https://importfunkologin.netlify.app/dashboard?token={token}&idUsuario={usuario.idUsuario}"
            return redirect(frontend_url)

        else:
            return Response({"error": "User data retrieval failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            usuario_autenticado = token.user  # Usuario autenticado según el token

            # Buscar el usuario por el ID pasado en la URL
            try:
                usuario_consultado = Usuario.objects.get(idUsuario=id)
            except Usuario.DoesNotExist:
                return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

            # Verificar que el usuario autenticado tiene permisos para ver estos datos
            if usuario_autenticado.idUsuario != usuario_consultado.idUsuario and not usuario_autenticado.is_staff:
                return Response({"error": "No autorizado."}, status=status.HTTP_403_FORBIDDEN)

            # Si tiene permiso, serializar y retornar los datos del usuario consultado
            serializer = UsuarioSerializer(instance=usuario_consultado)

            return Response({"Usuario": serializer.data}, status=status.HTTP_200_OK)

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

@api_view(["POST", "GET"])
def reseñas(request):

    if request.method == "POST":
        # Verifica si el usuario está autenticado
        usuario, error_response = userAuthorization(request)
        if error_response:
            return error_response  # Retorna error si la autenticación falla

        # Obtener datos del cuerpo de la petición
        data = request.data.copy()  # Copiamos los datos para evitar modificar request.data
        data["usuario"] = usuario.idUsuario  # Asigna el ID del usuario autenticado a la reseña

        # Validar que el contenido no esté vacío
        contenido = data.get("contenido", "").strip()
        if not contenido:
            return Response({"error": "El contenido de la reseña no puede estar vacío."}, status=status.HTTP_400_BAD_REQUEST)

        # Validar que el número de estrellas esté dentro del rango permitido (1-5)
        try:
            estrellas = int(data.get("estrellas"))
            if estrellas not in range(1, 6):
                return Response({"error": "El número de estrellas debe estar entre 1 y 5."}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({"error": "El número de estrellas debe ser un entero válido."}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica si el Funko existe antes de crear la reseña
        funko_id = data.get("funko")
        if funko_id and not Funko.objects.filter(idFunko=funko_id).exists():
            return Response({"error": "El Funko especificado no existe."}, status=status.HTTP_404_NOT_FOUND)

        # Serializar y guardar la reseña
        serializer = ReseñaSerializer(data=data)
        if serializer.is_valid():
            serializer.save(usuario=usuario)  # Pasamos el objeto usuario al guardar
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == "GET":
        # Listar todas las reseñas
        reseñas = Reseña.objects.all().order_by("-fecha")  # Ordenadas por fecha más reciente
        serializer = ReseñaSerializer(reseñas, many=True)
        
        # Modificar los datos para incluir el nombre de usuario en cada reseña
        response_data = []
        for reseña_data in serializer.data:
            reseña_obj = Reseña.objects.get(idReseña=reseña_data['idReseña'])
            reseña_data['nombre_usuario'] = reseña_obj.usuario.nombre
            response_data.append(reseña_data)
        
        return Response(response_data, status=status.HTTP_200_OK)

@api_view(["GET", "DELETE"])
def gestionar_reseña(request, id):
    # Verifica si el usuario está autenticado
    usuario, error_response = userAuthorization(request)
    if error_response:
        return error_response

    try:
        # Obtener la reseña por ID
        reseña = Reseña.objects.get(idReseña=id)
    except Reseña.DoesNotExist:
        return Response({"error": "Reseña no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        # Serializar y devolver la reseña
        serializer = ReseñaSerializer(reseña)

        # Crear un diccionario con los datos de la reseña y agregar el nombre del usuario
        response_data = serializer.data

        response_data['nombre_usuario'] = reseña.usuario.nombre
        return Response(response_data, status=status.HTTP_200_OK)

    elif request.method == "DELETE":
        # Verificar que el usuario sea dueño de la reseña antes de borrarla
        if reseña.usuario != usuario:
            return Response({"error": "No tienes permiso para borrar esta reseña."}, status=status.HTTP_403_FORBIDDEN)

        reseña.delete()
        return Response({"mensaje": "Reseña eliminada correctamente."}, status=status.HTTP_200_OK)

@api_view(["GET"])
def listar_favoritos(request):
    # Verifica la autenticación del usuario
    usuario, error_response = userAuthorization(request)
    if error_response:
        return error_response

    # Obtener los Funkos favoritos del usuario
    favoritos = usuario.favoritos.all()
    # Serializar los datos
    funko_serializer = FunkoSerializer(favoritos, many=True)

    # Modificar los datos antes de enviarlos
    funko_data = funko_serializer.data
    for funko in funko_data:
        # Obtener el objeto Funko correspondiente
        funko_obj = favoritos.get(idFunko=funko["idFunko"])

        # Si el Funko tiene categorías, las agregamos como lista de diccionarios con ID y nombre
        categorias = funko_obj.categoría.all()
        funko["categoría"] = [
            {"idCategoria": cat.idCategoria, "nombre": cat.nombre} for cat in categorias
        ] if categorias.exists() else []

        # Verificar si el Funko tiene una imagen
        if funko_obj.imagen:
            if isinstance(funko["imagen"], int):  
                # Si 'imagen' es solo un ID, convertirlo en un diccionario
                funko["imagen"] = {
                    "idImagen": funko["imagen"],
                    "clave": funko_obj.imagen.clave,
                    "url": funko_obj.imagen.url
                }
            else:
                # Si ya es un diccionario, agregar los valores
                funko["imagen"]["clave"] = funko_obj.imagen.clave
                funko["imagen"]["url"] = funko_obj.imagen.url

    return Response(
        {"funkos": funko_data},  # Retornar los funkos con categorías y clave de imagen
        status=status.HTTP_200_OK,
    )
    
    #return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
def listar_carrito(request, id):
    # Verifica autenticación del usuario
    usuario, error_response = userAuthorization(request)
    if error_response:
        return error_response

    # Verificar que el usuario autenticado es el mismo del ID solicitado
    if usuario.idUsuario != id:
        return Response({"error": "No tienes permiso para ver este carrito."}, status=status.HTTP_403_FORBIDDEN)

    try:
        # Buscar el carrito del usuario
        carrito = Carrito.objects.get(usuario=usuario)
    except Carrito.DoesNotExist:
        return Response({"error": "Carrito no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    # Obtener los items del carrito
    items = CarritoItem.objects.filter(carrito=carrito)

    # Serializar los datos
    serializer = CarritoItemSerializer(items, many=True)

    return Response({
        "idCarrito": carrito.idCarrito,
        "total": carrito.total,
        "items": serializer.data
    }, status=status.HTTP_200_OK)

@api_view(["GET"])
def listar_compras(request, id):
    # Verifica autenticación del usuario
    usuario, error_response = userAuthorization(request)
    if error_response:
        return error_response

    # Verificar que el usuario autenticado es el mismo del ID solicitado
    if usuario.idUsuario != id:
        return Response({"error": "No tienes permiso para ver estas compras."}, status=status.HTTP_403_FORBIDDEN)

    # Obtener las compras del usuario
    compras = Compra.objects.filter(usuario=usuario)

    # Serializar los datos
    serializer = CompraSerializer(compras, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
def listar_reseñas_usuario(request, id):
    # Verifica autenticación del usuario
    usuario, error_response = userAuthorization(request)
    if error_response:
        return error_response

    # Verificar que el usuario autenticado es el mismo del ID solicitado
    if usuario.idUsuario != id:
        return Response({"error": "No tienes permiso para ver estas reseñas."}, status=status.HTTP_403_FORBIDDEN)

    # Obtener las reseñas del usuario
    reseñas = Reseña.objects.filter(usuario=usuario)

    # Serializar los datos
    serializer = ReseñaSerializer(reseñas, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)
