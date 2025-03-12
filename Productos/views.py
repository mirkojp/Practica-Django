import json
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from Usuarios.models import Token, Usuario, Reseña
from Usuarios.serializers import ReseñaSerializer
from .models import Funko, Imagen
from .models import Descuento, FunkoDescuento, Categoría
from .serializers import FunkoSerializer, DescuentoSerializer, FunkoDescuentoSerializer, CategoríaSerializer,ImagenSerializer
from django.db import IntegrityError
from django.db import transaction
from Utils.tokenAuthorization import userAuthorization, adminAuthorization
from django.db.models import Q
from rest_framework.views import APIView
from decorators.token_decorators import token_required_admin_without_user
from .services import upload_image_to_cloudinary, delete_image_from_cloudinary
import cloudinary

@api_view(["POST", "GET"]) #Resuelve crear y listar funkos
def old_Funkos(request):

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

            # Verifica que la request tenga todos los datos necesarios
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

@api_view(["POST", "GET"])
def old_mirko_funkos(request):
    if request.method == "POST":
        # Obtener el token del encabezado de la solicitud
        token = request.headers.get("Authorization")

        if not token or not token.startswith("Token "):
            return Response(
                {"error": "Token no provisto o incorrecto."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Extraer el token después de la palabra 'Token '
        token_key = token.split(" ")[1]

        try:
            # Buscar el token en la base de datos
            token = Token.objects.get(key=token_key)
            usuario = token.user  # Obtener el usuario asociado al token

            # Verificar que el usuario es un admin
            if not usuario.is_staff:  # Sólo el usuario admin puede crear funkos
                return Response(
                    {"error": "No autorizado."}, status=status.HTTP_401_UNAUTHORIZED
                )

            # Verificar que la request tenga todos los datos necesarios
            serializer = FunkoSerializer(data=request.data)
            if serializer.is_valid():
                # Obtener la imagen desde la request (si la hay)
                image_file = request.FILES.get("imagen")

                if image_file:
                    # Subir la imagen a Cloudinary
                    image_data = upload_image_to_cloudinary(image_file)

                    # Verificar si hubo error en la carga de la imagen
                    if "error" in image_data:
                        return Response(
                            {"error": image_data["error"]},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )

                    # Iniciar la transacción atómica para garantizar ambas operaciones
                    try:
                        with transaction.atomic():
                            # Crear la imagen en la base de datos
                            imagen = Imagen.objects.create(
                                clave=image_data["clave"],
                                url=image_data["url"],
                                nombre=image_data["nombre"],
                                ancho=image_data["ancho"],
                                alto=image_data["alto"],
                                formato=image_data["formato"],
                            )

                            # Asignar la imagen al funko y guardar el funko
                            serializer.save(imagen=imagen)
                            funko = serializer.save()

                        return Response(
                            {
                                "Mensaje": "Recurso creado exitosamente",
                                "Funko": serializer.data,
                            },
                            status=status.HTTP_201_CREATED,
                        )
                    except IntegrityError:
                        return Response(
                            {"error": "Ya existe un Funko con ese nombre."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    except Exception as e:
                        return Response(
                            {"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )
                else:
                    # Si no hay imagen, se maneja como sin imagen asociada
                    serializer.validated_data["imagen"] = None
                    try:
                        with transaction.atomic():
                            # Crear el funko sin imagen
                            funko = serializer.save()

                        return Response(
                            {
                                "Mensaje": "Recurso creado exitosamente",
                                "Funko": serializer.data,
                            },
                            status=status.HTTP_201_CREATED,
                        )
                    except IntegrityError:
                        return Response(
                            {"error": "Ya existe un Funko con ese nombre."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    except Exception as e:
                        return Response(
                            {"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Token.DoesNotExist:
            return Response(
                {"error": "Token inválido o no encontrado."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    if request.method == 'GET':
        try:
            # Obtener todos los registros del modelo Funko, incluyendo las imágenes
            funkos = Funko.objects.all()  # Se obtienen todos los funkos con la relación de imagen
            funko_serializer = FunkoSerializer(funkos, many=True)

            return Response(
                {
                    "funkos": funko_serializer.data  # Retornar todos los funkos con sus imágenes
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST", "GET"])
def funkos(request):
    if request.method == "POST":
        token = request.headers.get("Authorization")

        if not token or not token.startswith("Token "):
            return Response(
                {"error": "Token no provisto o incorrecto."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token_key = token.split(" ")[1]

        try:
            token = Token.objects.get(key=token_key)
            usuario = token.user

            if not usuario.is_staff:
                return Response(
                    {"error": "No autorizado."}, status=status.HTTP_401_UNAUTHORIZED
                )

            serializer = FunkoSerializer(data=request.data)
            if serializer.is_valid():
                imagen_id = request.data.get("imagen")
                imagen = None
                if imagen_id:
                    try:
                        imagen = Imagen.objects.get(pk=imagen_id)
                    except Imagen.DoesNotExist:
                        return Response(
                            {"error": "Imagen no encontrada."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                try:
                    with transaction.atomic():
                        funko = serializer.save()
                        if imagen:
                            funko.imagen = imagen
                            funko.save()

                    return Response(
                        {
                            "Mensaje": "Recurso creado exitosamente",
                            "Funko": FunkoSerializer(funko).data,
                        },
                        status=status.HTTP_201_CREATED,
                    )
                except IntegrityError:
                    return Response(
                        {"error": "Ya existe un Funko con ese nombre."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                except Exception as e:
                    return Response(
                        {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Token.DoesNotExist:
            return Response(
                {"error": "Token inválido o no encontrado."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(["GET", "PUT", "DELETE"]) #Resuelve listar un funko, eliminarlo y modificarlo
def old_operaciones_funkos(request, id):

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
            # Verifica que la request tenga todos los datos necesarios
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
            # Borra el funko
            funko.delete()

            return Response(status=status.HTTP_200_OK)

    except Token.DoesNotExist:
        return Response({"error": "Token inválido o no encontrado."}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET", "PUT", "DELETE"])
def operaciones_funkos(request, id):
    try:
        funko = Funko.objects.get(idFunko=id)
    except Funko.DoesNotExist:
        return Response(
            {"error": "Funko no encontrado."}, status=status.HTTP_404_NOT_FOUND
        )
    except ValueError:
        return Response({"error": "ID no válido"}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "GET":
        serializer = FunkoSerializer(funko)
        return Response({"Funko": serializer.data}, status=status.HTTP_200_OK)

    # Verificar Token
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Token "):
        return Response(
            {"error": "Token no provisto o incorrecto."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token_key = token.split(" ")[1]
    try:
        token = Token.objects.get(key=token_key)
        usuario = token.user

        if not usuario.is_staff:
            return Response(
                {"error": "No autorizado."}, status=status.HTTP_401_UNAUTHORIZED
            )

        if request.method == "PUT":
            serializer = FunkoSerializer(funko, data=request.data, partial=True)
            if serializer.is_valid():
                nueva_imagen_id = request.data.get("imagen_id")

                if nueva_imagen_id:
                    try:
                        nueva_imagen = Imagen.objects.get(pk=nueva_imagen_id)

                        # Eliminar la imagen anterior en Cloudinary si existía
                        if funko.imagen:
                            delete_image_from_cloudinary(funko.imagen.clave)
                            funko.imagen.delete()

                        funko.imagen = nueva_imagen  # Asignar nueva imagen
                    except Imagen.DoesNotExist:
                        return Response(
                            {"error": "Imagen no encontrada."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                serializer.save()
                return Response(
                    {
                        "Mensaje": "Funko actualizado correctamente",
                        "Funko": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == "DELETE":
            funko.delete()  # Esto ahora borra el Funko y su imagen en BD y Cloudinary
            return Response(
                {"Mensaje": "Funko eliminado correctamente"}, status=status.HTTP_200_OK
            )

    except Token.DoesNotExist:
        return Response(
            {"error": "Token inválido."}, status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST", "DELETE"])  # Resuelve agregar un funko a fav del user
def favoritos(request, id):

    # Llama a userAuthorization para verificar el token y obtener el usuario
    usuario, error_response = userAuthorization(request)

    if error_response: # Retorna el error si el token es inválido o no encontrado
        return Response(error_response) 
    
    try:
        # Intenta obtener el Funko por su ID
        funko = Funko.objects.get(idFunko=id)
    except Funko.DoesNotExist:
        return Response({"error": "Funko no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == "POST":
        
        # Verifica si el Funko ya está en la lista de favoritos del usuario
        if usuario.favoritos.filter(idFunko=funko.idFunko).exists():
            return Response({"message": "Este Funko ya está en tu lista de favoritos."}, status=status.HTTP_200_OK)
        
        # Agrega el Funko a los favoritos del usuario
        usuario.favoritos.add(funko)
        return Response({"message": "Funko agregado a favoritos con éxito."}, status=status.HTTP_201_CREATED)
    
    elif request.method == "DELETE":

        # Verifica si el Funko no está en la lista de favoritos del usuario
        if not usuario.favoritos.filter(idFunko=funko.idFunko).exists():
            return Response({"message": "Este Funko no está en tu lista de favoritos."}, status=status.HTTP_200_OK)
        
        # Elimina el Funko de los favoritos del usuario
        usuario.favoritos.remove(funko)
        return Response({"message": "Funko eliminado de favoritos con éxito."}, status=status.HTTP_200_OK)


@api_view(["POST", "GET"])  
def descuentos(request):     #Resuelve crear y listar los descuentos

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
def op_funkoDescuentos(request, id):   #Resuelve listar un FunkoDescuento, eliminarlo y modificarlo

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

@api_view(["POST", "GET"])
def categorias(request):

    
    if request.method == 'POST':

        # Llama a userAuthorization para verificar el token y obtener el usuario
        usuario, error_response = adminAuthorization(request)

        if error_response: # Retorna el error si el token es inválido o no encontrado
            return error_response

        #Verifica que la request tenga todos los datos necesarios
        serializer = CategoríaSerializer(data=request.data)
        if serializer.is_valid():

            try:
                with transaction.atomic():
                    # Crear el descuento utilizando el método save del serializer
                    serializer.save()

                return Response(
                    {
                        "Categoria": serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                # Manejo de excepciones si hay un error de integridad
                return Response({"error": "Ya existe una Categoria con ese nombre."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                # Manejo de otras excepciones
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'GET':

        # Llama a userAuthorization para verificar el token y obtener el usuario
        usuario, error_response = userAuthorization(request)

        if error_response: # Retorna el error si el token es inválido o no encontrado
            return error_response

        try:
            # Serializar todos los registros del modelo Descuento
            categorias = Categoría.objects.all()
            serializer = CategoríaSerializer(categorias, many=True)


            return Response(
                {
                    "Categorias" : serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["DELETE", "PUT", "GET"])
def op_categorias(request, id):

    # Llama a userAuthorization para verificar el token y obtener el usuario
    usuario, error_response = adminAuthorization(request)

    if error_response: # Retorna el error si el token es inválido o no encontrado
        return error_response

    if request.method == 'GET': 
        try:
            # Intentar obtener la Categoria por el id
            categoria = Categoría.objects.get(idCategoria=id)
            serializer = CategoríaSerializer(categoria)

            return Response(
                {
                    "Categoria" : serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Categoría.DoesNotExist:
            return Response({"error": "Categoria no encontrada con ese ID."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            # Si el valor del ID no es válido (por ejemplo, si es una cadena en lugar de un número)
            return Response({"error": "ID no válido"},status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        # Verifica que la request tenga todos los datos necesarios
        serializer = CategoríaSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # Intentar obtener la Categoria por el id
                categoria = Categoría.objects.get(idCategoria=id)

                # Validar que no exista otra Categoria con el mismo nombre (excluyendo la actual)
                if Categoría.objects.filter(nombre=serializer.data["nombre"]).exclude(idCategoria=categoria.idCategoria).exists():
                    return Response(
                        {"error": "Ya existe una Categoria con el mismo nombre"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                categoria.nombre = serializer.data["nombre"]
                serializer = CategoríaSerializer(categoria)
                categoria.save()

                return Response(
                    {
                        "Mensaje": "Recurso actualizado correctamente",
                        "Categoria": serializer.data,
                    },
                    status=status.HTTP_200_OK
                )
            except Categoría.DoesNotExist:
                return Response({"error": "Categoria no encontrada con ese ID."}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                # Manejo de otras excepciones
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        try:
            # Intentar obtener la Categoria por el id
            categoria = Categoría.objects.get(idCategoria=id)
            categoria.delete()

            return Response(status=status.HTTP_200_OK)

        except Categoría.DoesNotExist:
            return Response({"error": "Categoria no encontrada con ese ID."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            # Si el valor del ID no es válido (por ejemplo, si es una cadena en lugar de un número)
            return Response({"error": "ID no válido"},status=status.HTTP_400_BAD_REQUEST)

# @token_required_admin_without_user
# class ImagenView(APIView):
#     def get(self, request, idImagen=None):
#         try:
#             if idImagen:
#                 imagen = get_object_or_404(Imagen, idImagen=idImagen)
#                 serializer = ImagenSerializer(imagen)
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             return Response(
#                 {"error": "ID de imagen no proporcionado"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         except Exception as e:
#             return Response(
#                 {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#     def post(self, request):
#         """Uploads the image to Cloudinary and saves the metadata in the database."""
#         try:
#             # Step 1: Generate Cloudinary signed URL
#             signature_data = generate_signature()
#             if "error" in signature_data:
#                 return Response(
#                     {"error": "Failed to generate Cloudinary signature"},
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 )

#             # Step 2: Get image file from request
#             image_file = request.FILES.get("image")  # The frontend must send the file
#             if not image_file:
#                 return Response(
#                     {"error": "No image file provided"},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             # Step 3: Upload image to Cloudinary
#             upload_response = cloudinary.uploader.upload(
#                 image_file,
#                 api_key=signature_data["api_key"],
#                 timestamp=signature_data["timestamp"],
#                 signature=signature_data["signature"],
#                 #upload_preset="your_upload_preset",  # Optional: If using unsigned uploads
#             )

#             # Step 4: Create image data dictionary
#             image_data = {
#                 "clave": upload_response["public_id"],  # Cloudinary identifier
#                 "url": upload_response["secure_url"],  # Cloudinary image URL
#                 "nombre": upload_response["original_filename"],  # Original filename
#                 "ancho": upload_response["width"],  # Image width
#                 "alto": upload_response["height"],  # Image height
#                 "formato": upload_response["format"],  # Image format
#             }

#             # Step 5: Validate and save in Django database
#             serializer = ImagenSerializer(data=image_data)
#             if serializer.is_valid():
#                 imagen = serializer.save()
#                 return Response(
#                     {
#                         "mensaje": "Imagen creada correctamente",
#                         "idImagen": imagen.idImagen,
#                         "image_url": imagen.url,  # Returning the image URL
#                     },
#                     status=status.HTTP_201_CREATED,
#                 )

#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             return Response(
#                 {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#     def put(self, request, idImagen):
#         """Updates an image, replacing the existing one in Cloudinary."""
#         try:
#             # Step 1: Retrieve the existing image
#             imagen = get_object_or_404(Imagen, idImagen=idImagen)
#             old_image_url = imagen.image_url  # Assuming this is the field storing the Cloudinary URL

#             # Step 2: If a new image is provided, delete the old one from Cloudinary
#             new_image = request.data.get("image")
#             if new_image and old_image_url:
#                 # Extract public_id from the Cloudinary URL
#                 public_id = old_image_url.split("/")[-1].split(".")[0]
#                 cloudinary.uploader.destroy(public_id)  # Delete old image

#             # Step 3: Update the database record with new data (including image)
#             serializer = ImagenSerializer(imagen, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(
#                     {"mensaje": "Imagen actualizada correctamente"},
#                     status=status.HTTP_200_OK,
#                 )
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             return Response(
#                 {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#     def delete(self, request, idImagen):
#         # check
#         try:
#             imagen = get_object_or_404(Imagen, idImagen=idImagen)
#             imagen.delete()
#             return Response(
#                 {"mensaje": "Imagen eliminada correctamente"},
#                 status=status.HTTP_204_NO_CONTENT,
#             )
#         except Exception as e:
#             return Response(
#                 {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


@api_view(["POST", "DELETE"])
def gestionar_funkos_categoria(request, id):
    # Verifica si el usuario es administrador
    usuario, error_response = adminAuthorization(request)
    if error_response:
        return error_response

    try:
        # Intenta obtener la categoría por ID
        categoria = Categoría.objects.get(idCategoria=id)
    except Categoría.DoesNotExist:
        return Response({"error": "Categoría no encontrada con ese ID."}, status=status.HTTP_404_NOT_FOUND)

    # Verifica que la solicitud tenga la lista de IDs de Funkos
    funkos_ids = request.data.get("funkos", [])
    if not isinstance(funkos_ids, list) or not funkos_ids:
        return Response({"error": "Debes proporcionar una lista de IDs de Funkos."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Filtra los Funkos que existen en la base de datos
        funkos = Funko.objects.filter(idFunko__in=funkos_ids)

        # Verifica si hay IDs que no existen
        ids_encontrados = set(funkos.values_list("idFunko", flat=True))
        ids_no_encontrados = set(funkos_ids) - ids_encontrados

        if ids_no_encontrados:
            return Response({"error": f"Algunos Funkos no existen: {list(ids_no_encontrados)}"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == "POST":
            # Agregar Funkos a la categoría
            categoria.funkos.add(*funkos)
            mensaje = "Funkos agregados correctamente a la categoría."
        elif request.method == "DELETE":
            # Eliminar Funkos de la categoría
            categoria.funkos.remove(*funkos)
            mensaje = "Funkos eliminados correctamente de la categoría."

        return Response(
            {
                "mensaje": mensaje,
                "categoria": CategoríaSerializer(categoria).data,
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def listar_reseñas_funko(request, id):
    # Verifica autenticación del usuario
    usuario, error_response = userAuthorization(request)
    if error_response:
        return error_response

    try:
        # Verifica que el Funko existe
        funko = Funko.objects.get(idFunko=id)
    except Funko.DoesNotExist:
        return Response({"error": "Funko no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    # Obtiene las reseñas del Funko
    reseñas = Reseña.objects.filter(funko=funko)

    # Serializa los datos
    serializer = ReseñaSerializer(reseñas, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

@token_required_admin_without_user
class ImagenListView(APIView):
    def post(self, request):
        if "imagen" not in request.FILES:
            return Response(
                {"error": "No se proporcionó ninguna imagen."},
                status=status.HTTP_400_BAD_REQUEST
            )

        imagen = request.FILES["imagen"]

        try:
            upload_response = cloudinary.uploader.upload(imagen)
            image_data = {
                "clave": upload_response["public_id"],
                "url": upload_response["secure_url"],
                "nombre": upload_response["original_filename"],
                "ancho": upload_response["width"],
                "alto": upload_response["height"],
                "formato": upload_response["format"],
            }

            imagen_obj = Imagen.objects.create(**image_data)
            serializer = ImagenSerializer(imagen_obj)

            return Response(
                {"Mensaje": "Imagen subida con éxito", "Imagen": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": f"Error al subir la imagen: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


    def get(self, request, imagen_id=None):
        if imagen_id:
            try:
                imagen = Imagen.objects.get(pk=imagen_id)
                serializer = ImagenSerializer(imagen)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Imagen.DoesNotExist:
                return Response(
                    {"error": "Imagen no encontrada"}, status=status.HTTP_404_NOT_FOUND
                )

        imagenes = Imagen.objects.all()
        serializer = ImagenSerializer(imagenes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, imagen_id):
        try:
            imagen = Imagen.objects.get(pk=imagen_id)
        except Imagen.DoesNotExist:
            return Response(
                {"error": "Imagen no encontrada"}, status=status.HTTP_404_NOT_FOUND
            )

        nueva_imagen = request.FILES.get("imagen")
        if not nueva_imagen:
            return Response(
                {"error": "No se ha proporcionado ninguna imagen nueva."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                # Eliminar la imagen anterior en Cloudinary
                delete_image_from_cloudinary(imagen.clave)

                # Subir la nueva imagen a Cloudinary
                image_data = upload_image_to_cloudinary(nueva_imagen)
                if "error" in image_data:
                    return Response(
                        {"error": image_data["error"]},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
                
                # Actualizar los datos de la imagen en la base de datos
                imagen.clave = image_data["clave"]
                imagen.url = image_data["url"]
                imagen.nombre = image_data["nombre"]
                imagen.ancho = image_data["ancho"]
                imagen.alto = image_data["alto"]
                imagen.formato = image_data["formato"]
                imagen.save()

            return Response(
                {"mensaje": "Imagen actualizada exitosamente", "imagen": ImagenSerializer(imagen).data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, imagen_id):
        try:
            imagen = Imagen.objects.get(pk=imagen_id)
        except Imagen.DoesNotExist:
            return Response(
                {"error": "Imagen no encontrada"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            with transaction.atomic():
            # Eliminar la imagen de Cloudinary
                delete_image_from_cloudinary(imagen.clave)

            # Eliminar la imagen de la base de datos
                imagen.delete()

            return Response(
                {"mensaje": "Imagen eliminada exitosamente"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
