from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from Usuarios.models import Token, Usuario
from .models import Funko
from .models import Descuento, FunkoDescuento
from .serializers import FunkoSerializer, DescuentoSerializer, FunkoDescuentoSerializer
from django.db import IntegrityError
from django.db import transaction
from Utils.tokenAuthorization import userAuthorization, adminAuthorization
from django.db.models import Q


# Create your views here.
@api_view(["POST", "GET"]) #Resuelve crear y listar funkos
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
    
@api_view(["GET", "PUT", "DELETE"]) #Resuelve listar un funko, eliminarlo y modificarlo
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

@api_view(["POST"])  # Resuelve agregar un funko a fav del user
def agregar_favorito(request, id):

    # Llama a userAuthorization para verificar el token y obtener el usuario
    usuario, error_response = userAuthorization(request)

    if error_response: # Retorna el error si el token es inválido o no encontrado
        return Response(error_response) 
    
    try:
        # Intenta obtener el Funko por su ID
        funko = Funko.objects.get(idFunko=id)
    except Funko.DoesNotExist:
        return Response({"error": "Funko no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    # Verifica si el Funko ya está en la lista de favoritos del usuario
    if usuario.favoritos.filter(idFunko=funko.idFunko).exists():
        return Response({"message": "Este Funko ya está en tu lista de favoritos."}, status=status.HTTP_200_OK)
    
    # Agrega el Funko a los favoritos del usuario
    usuario.favoritos.add(funko)
    return Response({"message": "Funko agregado a favoritos con éxito."}, status=status.HTTP_201_CREATED)


@api_view(["POST", "GET"])  
def descuentos(request):

    # Llama a userAuthorization para verificar el token y obtener el usuario
    usuario, error_response = adminAuthorization(request)

    if error_response: # Retorna el error si el token es inválido o no encontrado
        return error_response
    
    if request.method == 'POST':
        #Verifica que la request tenga todos los datos necesarios
        serializer = DescuentoSerializer(data=request.data)
        if serializer.is_valid():

            try:
                with transaction.atomic():
                    # Crear el descuento utilizando el método save del serializer
                    serializer.save()

                return Response(
                    {
                        "Descuento": serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )

            except Exception as e:
                # Manejo de otras excepciones
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'GET':
        try:
            # Serializar todos los registros del modelo Descuento
            descuentos = Descuento.objects.all()
            serializer = DescuentoSerializer(descuentos, many=True)


            return Response(
                {
                    "Descuentos" : serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["GET", "PUT", "DELETE"])
def operaciones_descuentos(request, id): #Resuelve listar un Descuento, eliminarlo y modificarlo

    # Llama a userAuthorization para verificar el token y obtener el usuario
    usuario, error_response = adminAuthorization(request)

    if error_response: # Retorna el error si el token es inválido o no encontrado
        return error_response
    
    if request.method == 'GET': 
        try:
            # Intentar obtener el Descuento por el id 
            descuento = Descuento.objects.get(idDescuento=id)
            serializer = DescuentoSerializer(descuento)

            return Response(
                {
                    "Descuento" : serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Descuento.DoesNotExist:
            return Response({"error": "Descuento encontrado con ese ID."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            # Si el valor del ID no es válido (por ejemplo, si es una cadena en lugar de un número)
            return Response({"error": "ID no válido"},status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == "PUT": #Modifica el funko segun el id

        #Verifica que la request tenga todos los datos necesarios
        serializer = DescuentoSerializer(data=request.data)
        if serializer.is_valid():
            try:
                
                # Intentar obtener el Descuento por el id 
                descuento = Descuento.objects.get(idDescuento=id)

                # Validar que no exista otro Descuento con el mismo porcentaje (excluyendo el actual)
                if Descuento.objects.filter(porcentaje=serializer.data["porcentaje"]).exclude(idDescuento=descuento.idDescuento).exists():
                    return Response(
                        {"error": "Ya existe un Descuento con un porcentaje identico."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                        
                descuento.porcentaje = serializer.data["porcentaje"]
                serializer = DescuentoSerializer(descuento)

                return Response(
                    {
                        "Mensaje": "Recurso actualizado correctamente",
                        "Descuento": serializer.data,
                    },
                    status=status.HTTP_200_OK
                )

            except Descuento.DoesNotExist:
                return Response({"error": "Descuento encontrado con ese ID."}, status=status.HTTP_404_NOT_FOUND)
            except ValueError:
                # Si el valor del ID no es válido (por ejemplo, si es una cadena en lugar de un número)
                return Response({"error": "ID no válido"},status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                # Manejo de otras excepciones
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  

    elif request.method == "DELETE":
        try:
            # Intentar obtener el Descuento por el id 
            descuento = Descuento.objects.get(idDescuento=id)
            descuento.delete()

            return Response(status=status.HTTP_200_OK)
        
        except Descuento.DoesNotExist:
            return Response({"error": "Descuento encontrado con ese ID."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            # Si el valor del ID no es válido (por ejemplo, si es una cadena en lugar de un número)
            return Response({"error": "ID no válido"},status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST", "GET"])
def funkoDescuentos(request):  #Resuelve crear FunkoDescuento y listarlos

    # Llama a userAuthorization para verificar el token y obtener el usuario
    usuario, error_response = adminAuthorization(request)

    if error_response: # Retorna el error si el token es inválido o no encontrado
        return error_response
    
    if request.method == "POST":

        # Verifica que la solicitud incluya los campos 'funko' y 'descuento' con sus respectivos IDs
        funko_id = request.data.get('funko')
        descuento_id = request.data.get('descuento')
        fecha_inicio = request.data.get('fecha_inicio')
        fecha_expiracion = request.data.get('fecha_expiracion')

        if not (funko_id and descuento_id and fecha_inicio and fecha_expiracion):
            return Response({"error": "Se requieren los campos 'funko', 'descuento', 'fecha_inicio' y 'fecha_expiracion'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Intenta obtener los objetos Funko y Descuento
            funko = Funko.objects.get(idFunko=funko_id)
            descuento = Descuento.objects.get(idDescuento=descuento_id)
        except Funko.DoesNotExist:
            return Response({"error": "Funko no encontrado con el ID proporcionado."}, status=status.HTTP_404_NOT_FOUND)
        except Descuento.DoesNotExist:
            return Response({"error": "Descuento no encontrado con el ID proporcionado."}, status=status.HTTP_404_NOT_FOUND)

        # Verificar si ya existe un FunkoDescuento en el mismo período o con solapamiento de fechas
        if FunkoDescuento.objects.filter(
                funko=funko,
                descuento=descuento,
            ).filter(
                Q(fecha_inicio__lte=fecha_expiracion) & Q(fecha_expiracion__gte=fecha_inicio)
            ).exists():
                return Response(
                    {"error": "Ya existe un FunkoDescuento para el mismo Funko y Descuento en este período o con fechas solapadas."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Crea el serializer de FunkoDescuento
        serializer = FunkoDescuentoSerializer(data={
            "funko": funko.idFunko,
            "descuento": descuento.idDescuento,
            "fecha_inicio": fecha_inicio,
            "fecha_expiracion": fecha_expiracion,
        })

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # Crear el FunkoDescuento utilizando el método save del serializer
                    serializer.save()

                return Response(
                    {
                        "Mensaje": "FunkoDescuento creado exitosamente.",
                        "FunkoDescuento": serializer.data,
                    },
                    status=status.HTTP_201_CREATED
                )

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "GET":

        # Obtener todos los registros del modelo FunkoDescuento
        funkoDescuentos = FunkoDescuento.objects.all().values("idFunkoDescuento", "fecha_inicio", "fecha_expiracion", "funko", "descuento")

        return Response(
            {
                funkoDescuentos
            },
            status=status.HTTP_200_OK
        )
    
@api_view(["DELETE", "PUT", "GET"])
def op_funkoDescuentos(request, id):

    # Llama a userAuthorization para verificar el token y obtener el usuario
    usuario, error_response = adminAuthorization(request)

    if error_response: # Retorna el error si el token es inválido o no encontrado
        return error_response

    if request.method == "DELETE":
        try:
            # Intentar obtener el FunkoDescuento por el id 
            funkoDescuento = FunkoDescuento.objects.get(idFunkoDescuento=id)
            funkoDescuento.delete()

            return Response(status=status.HTTP_200_OK)
        
        except FunkoDescuento.DoesNotExist:
            return Response({"error": "Descuento no encontrado con ese ID."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            # Si el valor del ID no es válido (por ejemplo, si es una cadena en lugar de un número)
            return Response({"error": "ID no válido"},status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == "PUT":
        # Intenta obtener el FunkoDescuento por su ID
        funko_descuento = get_object_or_404(FunkoDescuento, idFunkoDescuento=id)

        # Obtener el nuevo id del funko desde la request
        nuevo_funko_id = request.data.get('funko')

        # Si el nuevo funko es diferente del original, devuelve un error
        if nuevo_funko_id and nuevo_funko_id != funko_descuento.funko.idFunko:
            return Response({"error": "No puedes cambiar el Funko asociado a este descuento."}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica que la request tenga los datos necesarios
        serializer = FunkoDescuentoSerializer(funko_descuento, data=request.data)

        if serializer.is_valid():
            try:
                # Validar que no exista otro registro con el mismo funko y descuento en solapamiento de fechas
                fecha_inicio = serializer.validated_data.get('fecha_inicio')
                fecha_expiracion = serializer.validated_data.get('fecha_expiracion')
                funko = funko_descuento.funko
                descuento = funko_descuento.descuento

                overlapping = FunkoDescuento.objects.filter(
                    funko=funko
                ).exclude(idFunkoDescuento=funko_descuento.idFunkoDescuento).filter(
                    Q(fecha_inicio__lte=fecha_expiracion) & Q(fecha_expiracion__gte=fecha_inicio)
                ).exists()

                if overlapping:
                    return Response(
                        {"error": "Ya existe un FunkoDescuento con las mismas fechas para este Funko."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Guardar los cambios
                serializer.save()

                return Response(
                    {
                        "Mensaje": "FunkoDescuento actualizado correctamente.",
                        "FunkoDescuento": serializer.data,
                    },
                    status=status.HTTP_200_OK
                )

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == "GET":
        try:
            # Intentar obtener el FunkoDescuento por el id 
            funkoDescuento = FunkoDescuento.objects.get(idFunkoDescuento=id)
            serializer = FunkoDescuentoSerializer(funkoDescuento)

            return Response(
                {
                    "Descuento" : serializer.data
                },
                status=status.HTTP_200_OK
            )
        except FunkoDescuento.DoesNotExist:
            return Response({"error": "FunkoDescuento no encontrado con ese ID."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            # Si el valor del ID no es válido (por ejemplo, si es una cadena en lugar de un número)
            return Response({"error": "ID no válido"},status=status.HTTP_400_BAD_REQUEST)