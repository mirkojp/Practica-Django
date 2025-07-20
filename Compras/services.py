import json
import hmac
import hashlib

def validate_signature(body, signature, secret):
    """
    Validate the x-signature header to ensure the request is from MercadoPago.
    """
    try:
        # Split the x-signature header (e.g., "ts=123456,v1=abc123")
        signature_parts = dict(part.split("=") for part in signature.split(","))
        timestamp = signature_parts.get("ts")
        expected_signature = signature_parts.get("v1")

        # Compute the expected signature
        payload = f"id:{json.loads(body.decode('utf-8')).get('id')};ts:{timestamp};"
        computed_signature = hmac.new(
            secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        # Compare signatures
        return hmac.compare_digest(computed_signature, expected_signature)
    except Exception:
        return False
