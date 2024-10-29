from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Task
from django.utils import timezone

User = get_user_model()

class TaskModelTest(TestCase):
    
    def setUp(self):
        # Crear un usuario de prueba para asociar las tareas
        self.user = User.objects.create_user(username="testuser", password="testpassword")

    def test_task_creation(self):
        """Prueba que se pueda crear una tarea con los valores iniciales."""
        task = Task.objects.create(
            title="Tarea de prueba",
            description="Esta es una descripción de prueba",
            status="pending",
            user=self.user
        )
        self.assertEqual(task.title, "Tarea de prueba")
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.user, self.user)
        self.assertIsNone(task.completion_date)  # Al inicio no debe tener fecha de finalización

    def test_task_status_update_to_completed(self):
        """Prueba que al cambiar el estado a 'completed', se establezca la fecha de finalización."""
        task = Task.objects.create(
            title="Tarea de prueba",
            description="Esta es una descripción de prueba",
            status="in_progress",
            user=self.user
        )
        # Cambiar el estado a 'completed' y guardar
        task.status = "completed"
        task.save()

        # Verificar que completion_date se haya actualizado automáticamente
        self.assertEqual(task.status, "completed")
        self.assertIsNotNone(task.completion_date)
        # La fecha de finalización debe estar cercana a la fecha actual
        self.assertAlmostEqual(task.completion_date, timezone.now(), delta=timezone.timedelta(seconds=1))

    def test_task_deletion(self):
        """Prueba que se pueda eliminar una tarea y que no afecte a otras tareas del usuario."""
        task1 = Task.objects.create(title="Tarea 1", user=self.user)
        task2 = Task.objects.create(title="Tarea 2", user=self.user)
        
        # Verificar que ambas tareas existen
        self.assertEqual(Task.objects.filter(user=self.user).count(), 2)
        
        # Eliminar una tarea
        task1.delete()
        
        # Verificar que solo quede una tarea
        self.assertEqual(Task.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Task.objects.filter(user=self.user).first().title, "Tarea 2")
