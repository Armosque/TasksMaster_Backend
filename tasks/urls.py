from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet  # Importamos el TaskViewSet

# Creamos un router de DRF para las rutas automáticas
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')  

urlpatterns = [
    path('', include(router.urls))
]
