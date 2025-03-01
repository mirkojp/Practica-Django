import cloudinary
import cloudinary.utils
from datetime import datetime


def generate_signature() -> dict:
    """
    Genera una URL de carga para Cloudinary.
    """
    try:
        config = cloudinary.config()
        if not all([config.api_secret, config.api_key, config.cloud_name]):
            raise ValueError(
                "Faltan credenciales de Cloudinary. Verifica tu configuración."
            )

        timestamp = int(datetime.now().timestamp())  # Ensure it's an integer
        params_to_sign = {"timestamp": timestamp}
        signature = cloudinary.utils.api_sign_request(params_to_sign, config.api_secret)

        return {
            "signature": signature,
            "api_key": config.api_key,
            "timestamp": timestamp,
            "upload_url": f"https://api.cloudinary.com/v1_1/{config.cloud_name}/image/upload",
        }
    except Exception as e:
        return {"error": str(e)}
