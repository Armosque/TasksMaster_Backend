
from rest_framework import viewsets
from .models import Task
from .serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]  # Solo usuarios autenticados pueden acceder

    # Sobrescribimos get_queryset para que un usuario solo vea sus propias tareas
    def get_queryset(self):
        # Filtra las tareas que pertenecen al usuario autenticado
        queryset = Task.objects.filter(user=self.request.user)
        
        # Obtiene el parámetro de estado de la consulta
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)  # Filtra por estado si está presente

        return queryset
    
    # Sobrescribimos el método perform_create para asignar el usuario automáticamente
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
