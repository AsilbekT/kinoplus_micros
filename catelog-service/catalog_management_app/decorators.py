from functools import wraps
from django.http import JsonResponse
import jwt
from django.conf import settings
from django.core.exceptions import PermissionDenied

def check_authorization_header(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or ' ' not in auth_header:
            return JsonResponse({"message": "No valid token provided"}, status=403)

        token_type, token = auth_header.split(' ', 1)

        if token_type.lower() == 'bearer':
            try:
                payload = jwt.decode(token, settings.SECRET_KEY_JWT, algorithms=["HS256"])
                request.user_payload = payload
                if not 'is_admin' in payload:
                    return JsonResponse({"message": "Only admins can view this"}, status=401)
                    
            except jwt.ExpiredSignatureError:
                return JsonResponse({"message": "Token has expired"}, status=401)
            except (jwt.InvalidTokenError, jwt.DecodeError):
                return JsonResponse({"message": "Invalid token"}, status=401)

            # Continue processing the request
            return view_func(request, *args, **kwargs)
        
        elif token_type.lower() == 'token':
            return view_func(request, *args, **kwargs)
        
        return JsonResponse({"message": "Invalid token type"}, status=403)


    return _wrapped_view
