import json
import hmac
import hashlib

import json
import hmac
import hashlib


def validate_signature(body, signature, secret, mp_id, x_request_id=None,):
    """
    Validate the x-signature header to ensure the request is from MercadoPago.
    Idk why but it doesnt work for somethings

    Args:
        body: The raw request body (bytes).
        signature: The x-signature header (e.g., "ts=123456,v1=abc123").
        secret: The signing secret from Mercado Pago.
        mp_id = id from the transaction, 
        x_request_id: The x-request-id header 

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    try:
        # Split the x-signature header (e.g., "ts=123456,v1=abc123")
        signature_parts = dict(part.split("=") for part in signature.split(","))
        timestamp = signature_parts.get("ts")
        expected_signature = signature_parts.get("v1")

        if not timestamp or not expected_signature:
            return False

        if not mp_id:
            return False

        # Ensure mp_id is lowercase if alphanumeric
        mp_id = str(mp_id).lower() if str(mp_id).isalnum() else str(mp_id)

        # Build the payload dynamically based on available parameters
        payload_parts = []
        if mp_id:
            payload_parts.append(f"id:{mp_id}")
        if x_request_id:
            payload_parts.append(f"request-id:{x_request_id}")
        if timestamp:
            payload_parts.append(f"ts:{timestamp}")

        # Join the parts with semicolons and ensure trailing semicolon
        payload = ";".join(payload_parts) + ";"

        # Compute the HMAC-SHA256 signature
        computed_signature = hmac.new(
            secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        # Compare signatures securely
        return hmac.compare_digest(computed_signature, expected_signature)
    except Exception as e:
        print(f"Error validating signature: {e}")
        return False
