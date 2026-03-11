# recetas/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecetaViewSet, RegistroView # Asegúrate de que estos sean los nombres en tu views.py

router = DefaultRouter()
router.register(r'recetas', RecetaViewSet, basename='receta')

urlpatterns = [
    # Rutas del ViewSet (incluye /recetas/, /recetas/1/, /recetas/1/valorar/, etc.)
    path('', include(router.urls)),
    
    # Ruta manual para el registro (no es un ViewSet, es una Generic View)
    path('registro/', RegistroView.as_view(), name='registro'),
]