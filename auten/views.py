from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User
import jwt, datetime

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data['email']
        password = request.data["password"]
        
        user = User.objects.filter(email=email).first()
        
        if user is None:
            raise AuthenticationFailed("Usuario no encontrado")
        
        if not user.check_password(password):
            raise AuthenticationFailed("Password incorrecto")
        
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        
        # Usa "secret" para codificar el token
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        
        response = Response()
        response.set_cookie('jwt', token, httponly=True)
        
        response.data = {
            "jwt": token 
        }
        
        return response
    
class UserView(APIView):
    # Cambia a IsAuthenticated para proteger esta vista
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        token = request.headers.get("Authorization")

        if not token:
            raise AuthenticationFailed("Usuario no autenticado")
        
        # Procesar token del encabezado
        try:
            token_type, token = token.split()
            if token_type.lower() != 'bearer':
                raise AuthenticationFailed("Tipo de token no válido")
        except ValueError:
            raise AuthenticationFailed("Encabezado de autorización mal formado")

        try:
            # Usa "secret" para decodificar el token
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token ha expirado")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Token inválido")

        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            raise AuthenticationFailed("Usuario no encontrado")

        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        token = request.headers.get("Authorization")

        if not token:
            raise AuthenticationFailed("Usuario no autenticado")

        try:
            token_type, token = token.split()
            if token_type.lower() != 'bearer':
                raise AuthenticationFailed("Tipo de token no válido")
        except ValueError:
            raise AuthenticationFailed("Encabezado de autorización mal formado")

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token ha expirado")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Token inválido")

        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            raise AuthenticationFailed("Usuario no encontrado")

        # Actualizar otros datos del usuario
        if 'name' in request.data:
            user.name = request.data['name']
        if 'email' in request.data:
            user.email = request.data['email']

        # Si se incluye la contraseña en los datos, la encripta usando set_password
        if 'password' in request.data:
            user.set_password(request.data['password'])

        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)

class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Has cerrado sesión'
        }
        return response
