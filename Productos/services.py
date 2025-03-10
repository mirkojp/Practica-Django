import cloudinary
import cloudinary.utils
from datetime import datetime

# Deprecated
# def generate_signature() -> dict:
#     """
#     Genera una URL de carga para Cloudinary.
#     """
#     try:
#         config = cloudinary.config()
#         if not all([config.api_secret, config.api_key, config.cloud_name]):
#             raise ValueError(
#                 "Faltan credenciales de Cloudinary. Verifica tu configuración."
#             )

#         timestamp = int(datetime.now().timestamp())  # Ensure it's an integer
#         params_to_sign = {"timestamp": timestamp}
#         signature = cloudinary.utils.api_sign_request(params_to_sign, config.api_secret)

#         return {
#             "signature": signature,
#             "api_key": config.api_key,
#             "timestamp": timestamp,
#             "upload_url": f"https://api.cloudinary.com/v1_1/{config.cloud_name}/image/upload",
#         }
#     except Exception as e:
#         return {"error": str(e)}


def upload_image_to_cloudinary(image_file):
    """Sube una imagen a Cloudinary y devuelve los datos necesarios."""
    try:
        upload_response = cloudinary.uploader.upload(image_file)
        return {
            "clave": upload_response["public_id"],
            "url": upload_response["secure_url"],
            "nombre": upload_response["original_filename"],
            "ancho": upload_response["width"],
            "alto": upload_response["height"],
            "formato": upload_response["format"],
        }
    except Exception as e:
        return {"error": f"Error subiendo imagen a Cloudinary: {str(e)}"}


def delete_image_from_cloudinary(public_id):
    """Elimina una imagen de Cloudinary usando su ID."""
    try:
        cloudinary.uploader.destroy(public_id)
    except Exception as e:
        print(f"Error eliminando imagen de Cloudinary: {str(e)}")
