from rest_framework.test import APITestCase
from .models import Task
from .serializers import TaskSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class TaskSerializerTest(APITestCase):
    
    def setUp(self):
        # Crear un usuario y una tarea de ejemplo para las pruebas
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.task = Task.objects.create(
            title="Tarea de prueba",
            description="Descripción de prueba",
            status="pending",
            user=self.user
        )

    def test_serialized_data_contains_correct_fields(self):
        """Prueba que los datos serializados contengan los campos correctos."""
        serializer = TaskSerializer(instance=self.task)
        data = serializer.data
        
        # Verificar que los campos serializados son los especificados en fields
        self.assertEqual(set(data.keys()), {'id', 'title', 'description', 'status'})

    def test_read_only_fields(self):
        """Prueba que los campos de solo lectura no se puedan modificar."""
        data = {
            "title": "Tarea Modificada",
            "status": "completed",
            "created_at": "2023-10-10T10:00:00Z",
            "updated_at": "2023-10-10T10:00:00Z",
            "completion_date": "2023-10-10T10:00:00Z"
        }
        serializer = TaskSerializer(instance=self.task, data=data, partial=True)
        
        self.assertTrue(serializer.is_valid())
        task = serializer.save()

        # Verificar que los campos de solo lectura no hayan cambiado
        self.assertNotEqual(task.created_at, data["created_at"])
        self.assertNotEqual(task.updated_at, data["updated_at"])
        self.assertNotEqual(task.completion_date, data["completion_date"])

    def test_required_fields(self):
        """Prueba que el serializador requiere los campos obligatorios."""
        data = {
            "description": "Descripción sin título",  # Falta el campo title
            "status": "pending"
        }
        serializer = TaskSerializer(data=data)
        
        # Verificar que el campo "title" es requerido y no está presente en los datos
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_status_field_choices(self):
        """Prueba que el campo 'status' solo acepte valores válidos."""
        data = {
            "title": "Nueva Tarea",
            "description": "Descripción",
            "status": "invalid_status"  # Estado inválido
        }
        serializer = TaskSerializer(data=data)
        
        # Verificar que el campo "status" solo acepte opciones válidas
        self.assertFalse(serializer.is_valid())
        self.assertIn("status", serializer.errors)
