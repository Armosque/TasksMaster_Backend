import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Intenta obtener el token desde el encabezado Authorization
        auth_header = request.headers.get('Authorization')
        token = None
        
        if auth_header:
            try:
                token_type, token = auth_header.split()
                if token_type.lower() != 'bearer':
                    raise AuthenticationFailed('Tipo de token incorrecto')
            except ValueError:
                raise AuthenticationFailed('Encabezado de autorización mal formado')

        # Si no está en el encabezado, intenta obtener el token desde la cookie
        if not token:
            token = request.COOKIES.get('jwt')

        if not token:
            return None

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token ha expirado')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Token inválido')

        user = User.objects.filter(id=payload['id']).first()

        if user is None:
            raise AuthenticationFailed('Usuario no encontrado')

        return (user, None)
