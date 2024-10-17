from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from Usuarios.models import Token, Usuario
from .models import Funko
from .serializers import FunkoSerializer
from django.db import IntegrityError
from django.db import transaction


# Create your views here.
@api_view(["POST", "GET"])
def funkos(request):

    if request.method == 'POST':
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

            # Verificar que el usuario es un admin
            if not usuario.is_staff:  # Sólo el usuario admin puede crear funkos
                return Response({"error": "No autorizado."}, status=status.HTTP_401_UNAUTHORIZED)
            
            #Verifica que la request tenga todos los datos necesarios
            serializer = FunkoSerializer(data=request.data)
            if serializer.is_valid():

                try:
                    with transaction.atomic():
                        # Crear el funko utilizando el método save del serializer
                        serializer.save()

                    return Response(
                        {
                            "Mensaje": "Recurso creado exitosamente",
                            "Funko": serializer.data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                except IntegrityError:
                    # Manejo de excepciones si hay un error de integridad
                    return Response({"error": "Ya existe un Funko con ese nombre."}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    # Manejo de otras excepciones
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Token.DoesNotExist:
            return Response({"error": "Token inválido o no encontrado."}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'GET':
        # Obtener todos los registros del modelo Funko
        funkos = Funko.objects.all().values("idFunko", "nombre", "descripción", "is_backlight", "stock", "precio")

        return Response(
            {
                funkos
            },
            status=status.HTTP_200_OK
        )
    
@api_view(["GET", "PUT", "DELETE"])
def operaciones_funkos(request, id):

    try:
        # Intentar obtener el Funko por el id proporcionado
        funko = Funko.objects.get(idFunko=id)
        serializer = FunkoSerializer(funko)
    
    except Funko.DoesNotExist:
        # Si el Funko con el ID proporcionado no existe
        return Response(
            {"error": "Funko no encontrado con ese ID."},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValueError:
        # Si el valor del ID no es válido (por ejemplo, si es una cadena en lugar de un número)
        return Response(
            {"error": "ID no válido"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if request.method == 'GET': #Listar funko segun id
        return Response(
            {
                "Funko" : serializer.data
            },
            status=status.HTTP_200_OK
        )
    
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

        # Verificar que el usuario es un admin
        if not usuario.is_staff:  # Sólo el usuario admin puede crear funkos
            return Response({"error": "No autorizado."}, status=status.HTTP_401_UNAUTHORIZED)
        
        if request.method == 'PUT': #Modifica el funko segun id
            #Verifica que la request tenga todos los datos necesarios
            serializer = FunkoSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    
                    # Validar que no exista otro Funko con el mismo nombre (excluyendo el actual)
                    if Funko.objects.filter(nombre=serializer.data["nombre"]).exclude(idFunko=funko.idFunko).exists():
                        return Response(
                            {"error": "Ya existe un Funko con este nombre."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                        
                    funko.nombre = serializer.data["nombre"]
                    funko.descripción = serializer.data["descripción"]
                    funko.is_backlight = serializer.data["is_backlight"]
                    funko.stock = serializer.data["stock"]
                    funko.precio = serializer.data["precio"]
                        

                    return Response(
                        {
                            "Mensaje": "Recurso actualizado correctamente",
                            "Funko": serializer.data,
                        },
                        status=status.HTTP_200_OK,
                    )
                except Exception as e:
                    # Manejo de otras excepciones
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
        elif request.method == 'DELETE': #Borrar funko segun id
            #Borra el funko
            funko.delete()

            return Response(status=status.HTTP_200_OK)

    except Token.DoesNotExist:
            return Response({"error": "Token inválido o no encontrado."}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

