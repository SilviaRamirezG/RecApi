from django.shortcuts import render

# Create your views here.

# recetas/views.py

from rest_framework import viewsets, permissions
from .models import Receta
from .serializers import RecetaSerializer

class RecetaViewSet(viewsets.ModelViewSet):
    """
    Este ViewSet proporciona automáticamente las acciones:
    list (GET), create (POST), retrieve (GET id), 
    update (PUT), y destroy (DELETE).
    """
    queryset = Receta.objects.all()
    serializer_class = RecetaSerializer
    permission_classes = [permissions.IsAuthenticated]