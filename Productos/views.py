from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from Usuarios.models import Token, Usuario
from .serializers import FunkoSerializer
from django.db import IntegrityError
from django.db import transaction


# Create your views here.
@api_view(["POST"])
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

