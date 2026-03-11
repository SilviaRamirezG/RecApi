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
    # CORRECCIÓN AQUÍ: El método correcto es has_object_permission (no path_object_permission)
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Verifica que el campo 'creado_por' del modelo coincida con el usuario
        return obj.creado_por == request.user

# --- 2. VISTA DE REGISTRO ---
class RegistroView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegistroSerializer

# --- 3. VIEWSET DE RECETAS ---
class RecetaViewSet(viewsets.ModelViewSet):
    queryset = Receta.objects.all()
    serializer_class = RecetaSerializer
    
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
            # Verificamos si el usuario ya valoró (solo si está autenticado)
            if request.user.is_authenticated:
                val = Valoracion.objects.filter(autor=request.user, receta=receta).first()
                serializer = ValoracionSerializer(val) if val else ValoracionSerializer()
                return Response(serializer.data)
            return Response({"detail": "Debes estar logueado para ver tu valoración."}, status=401)

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
            if request.user.is_authenticated:
                # OJO: Cambié 'autor' por 'user' si tu modelo Favorito usa ese nombre
                existe = Favorito.objects.filter(user=request.user, receta=receta).exists()
                return Response({'es_favorito': existe})
            return Response({"es_favorito": False})

        serializer = FavoritoActionSerializer(data=request.data)
        if serializer.is_valid():
            quiere_favorito = serializer.validated_data.get('es_favorito', True)
            
            if quiere_favorito:
                # Asegúrate de si tu modelo Favorito usa el campo 'autor' o 'user'
                Favorito.objects.get_or_create(user=request.user, receta=receta)
                return Response({'status': 'Añadido a favoritos'}, status=status.HTTP_201_CREATED)
            else:
                Favorito.objects.filter(user=request.user, receta=receta).delete()
                return Response({'status': 'Eliminado de favoritos'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)