from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import User
import jwt

class AuthTest(APITestCase):
    
    def setUp(self):
        # Crear un usuario de prueba para las pruebas de autenticación
        self.user = User.objects.create_user(email="testuser@example.com", password="testpassword")
        self.login_url = reverse("login")
        self.register_url = reverse("register")
        self.user_url = reverse("user-detail")
        self.logout_url = reverse("logout")

    def test_register_user(self):
        """Prueba el registro de un nuevo usuario."""
        data = {
            "email": "newuser@example.com",
            "password": "newpassword"
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"], "newuser@example.com")

    def test_login_user(self):
        """Prueba el inicio de sesión de un usuario y la generación del token JWT."""
        data = {
            "email": "testuser@example.com",
            "password": "testpassword"
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("jwt", response.data)

    def test_access_protected_user_view(self):
        """Prueba que un usuario autenticado pueda ver sus datos con el token JWT."""
        # Iniciar sesión para obtener el token
        login_response = self.client.post(self.login_url, {"email": "testuser@example.com", "password": "testpassword"})
        token = login_response.data["jwt"]

        # Agregar el token en el encabezado Authorization
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        # Hacer solicitud a la vista protegida
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "testuser@example.com")

    def test_update_user_profile(self):
        """Prueba que un usuario autenticado pueda actualizar su perfil."""
        # Iniciar sesión para obtener el token
        login_response = self.client.post(self.login_url, {"email": "testuser@example.com", "password": "testpassword"})
        token = login_response.data["jwt"]

        # Agregar el token en el encabezado Authorization
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        # Datos para actualizar el perfil
        update_data = {
            "email": "updateduser@example.com",
            "password": "newpassword123"
        }
        
        response = self.client.put(self.user_url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "updateduser@example.com")

    def test_logout_user(self):
        """Prueba que un usuario pueda cerrar sesión y eliminar su token JWT."""
        # Iniciar sesión para obtener el token
        login_response = self.client.post(self.login_url, {"email": "testuser@example.com", "password": "testpassword"})
        token = login_response.data["jwt"]

        # Agregar el token en el encabezado Authorization
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        # Cerrar sesión
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Has cerrado sesión")

