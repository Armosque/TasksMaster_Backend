from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()

class TaskViewSetTest(APITestCase):
    
    def setUp(self):
        # Crear usuarios de prueba
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        
        # Crear tareas para el usuario1
        self.task1 = Task.objects.create(title="Tarea 1", description="Desc 1", status="pending", user=self.user1)
        self.task2 = Task.objects.create(title="Tarea 2", description="Desc 2", status="completed", user=self.user1)
        
        # URL para la vista de tareas
        self.url = reverse("task-list")  # Ajusta el nombre según tus rutas en urls.py

    def test_get_own_tasks(self):
        """Prueba que el usuario solo pueda ver sus propias tareas."""
        self.client.login(username="user1", password="password123")
        response = self.client.get(self.url)
        
        # Asegura que solo se devuelvan las tareas del usuario autenticado (user1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # user1 tiene 2 tareas
        self.assertEqual(response.data[0]["title"], "Tarea 1")

    def test_get_tasks_filtered_by_status(self):
        """Prueba el filtro por estado de las tareas."""
        self.client.login(username="user1", password="password123")
        
        # Filtrar tareas con estado 'completed'
        response = self.client.get(self.url, {'status': 'completed'})
        
        # Asegura que solo se devuelvan las tareas completadas
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Solo una tarea está completada
        self.assertEqual(response.data[0]["status"], "completed")

    def test_create_task(self):
        """Prueba la creación de una tarea y la asignación automática del usuario."""
        self.client.login(username="user1", password="password123")
        data = {"title": "Nueva Tarea", "description": "Descripción de la nueva tarea", "status": "in_progress"}
        response = self.client.post(self.url, data, format="json")
        
        # Asegura que la tarea fue creada y pertenece al usuario autenticado
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.filter(user=self.user1).count(), 3)  # user1 ahora tiene 3 tareas
        self.assertEqual(response.data["title"], "Nueva Tarea")
        self.assertEqual(response.data["status"], "in_progress")

    def test_user_cannot_access_others_tasks(self):
        """Prueba que un usuario no pueda ver tareas de otro usuario."""
        self.client.login(username="user2", password="password123")
        response = self.client.get(self.url)
        
        # user2 no debe ver las tareas de user1
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # user2 no tiene tareas
