from rest_framework.response import Response
from rest_framework import status
from Usuarios.models import Token

def userAuthorization(request):
    # Obtener el token del encabezado de la solicitud
    token = request.headers.get('Authorization')

    # Verificar si el token está presente y comienza con "Token "
    if not token or not token.startswith('Token '):
        return None, Response({"error": "Token no provisto o incorrecto."}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Extraer el token después de la palabra 'Token '
    token_key = token.split(' ')[1]
    
    try:
        # Buscar el token en la base de datos
        token = Token.objects.get(key=token_key)
        usuario = token.user  # Obtener el usuario asociado al token
        return usuario, None
        
    except Token.DoesNotExist:
        return None, Response({"error": "Token inválido o no encontrado."}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return None, Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def adminAuthorization(request):
    # Llama a tokenAuthorization para verificar el token y obtener el usuario
    usuario, error_response = userAuthorization(request)
    
    if error_response:
        return None, error_response  # Retorna el error si el token es inválido o no encontrado
    
    # Verifica si el usuario es administrador
    if not usuario.is_staff:
        return None, Response({"error": "Permiso denegado. Se requiere rol de administrador."}, status=status.HTTP_403_FORBIDDEN)
    
    return usuario, None  # Retorna el usuario si es administrador y está autenticado correctamente
