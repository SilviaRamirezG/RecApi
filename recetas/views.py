from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, status, authentication
from rest_framework.decorators import action
from rest_framework.response import Response

# Importaciones de tu proyecto
from .models import Receta, Valoracion, Favorito
from .serializers import (
    RecetaSerializer, 
    RegistroSerializer, 
    ValoracionSerializer, 
    FavoritoActionSerializer
)

# --- 1. PERMISOS PERSONALIZADOS ---
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permite leer a todos, pero solo el dueño puede editar o eliminar.
    """
    def path_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Verifica que el campo 'creado_por' del modelo coincida con el usuario
        return obj.creado_por == request.user

# --- 2. VISTA DE REGISTRO (Del Código 1) ---
class RegistroView(generics.CreateAPIView):
    """
    Endpoint público para que nuevos usuarios se den de alta.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegistroSerializer

# --- 3. VIEWSET DE RECETAS (Del Código 2) ---
class RecetaViewSet(viewsets.ModelViewSet):
    """
    Gestión completa de Recetas: CRUD + Valoraciones + Favoritos.
    """
    queryset = Receta.objects.all()
    serializer_class = RecetaSerializer
    
    # Combinación de autenticación y permisos
    authentication_classes = [
        authentication.SessionAuthentication, 
        authentication.BasicAuthentication
    ]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    # --- ACCIÓN: VALORAR ---
    @action(detail=True, methods=['get', 'post'], serializer_class=ValoracionSerializer)
    def valorar(self, request, pk=None):
        receta = self.get_object()
        
        if request.method == 'GET':
            val = Valoracion.objects.filter(autor=request.user, receta=receta).first()
            serializer = ValoracionSerializer(val) if val else ValoracionSerializer()
            return Response(serializer.data)

        serializer = ValoracionSerializer(data=request.data)
        if serializer.is_valid():
            puntuacion = serializer.validated_data['puntuacion']
            Valoracion.objects.update_or_create(
                autor=request.user, 
                receta=receta,
                defaults={'puntuacion': puntuacion}
            )
            return Response({'status': 'Valoración guardada'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- ACCIÓN: FAVORITOS ---
    @action(detail=True, methods=['get', 'post'], serializer_class=FavoritoActionSerializer)
    def favorito(self, request, pk=None):
        receta = self.get_object()
        
        if request.method == 'GET':
            existe = Favorito.objects.filter(autor=request.user, receta=receta).exists()
            return Response({'es_favorito': existe})

        serializer = FavoritoActionSerializer(data=request.data)
        if serializer.is_valid():
            quiere_favorito = serializer.validated_data.get('es_favorito', True)
            
            if quiere_favorito:
                Favorito.objects.get_or_create(autor=request.user, receta=receta)
                return Response({'status': 'Añadido a favoritos'}, status=status.HTTP_201_CREATED)
            else:
                Favorito.objects.filter(autor=request.user, receta=receta).delete()
                return Response({'status': 'Eliminado de favoritos'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)