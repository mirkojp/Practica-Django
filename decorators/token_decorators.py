from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from Utils.tokenAuthorization import userAuthorization, adminAuthorization

def token_required_admin(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        usuario, error_response = adminAuthorization(request)

        if error_response:
            return error_response 
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def token_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        usuario, response = userAuthorization(request)
        if response is not None:
            return response
        return view_func(request, *args, **kwargs)

    return _wrapped_view
