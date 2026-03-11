from rest_framework import viewsets, permissions, status, authentication
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Receta, Valoracion, Favorito
from .serializers import RecetaSerializer, ValoracionSerializer, FavoritoActionSerializer 

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creado_por == request.user

class RecetaViewSet(viewsets.ModelViewSet):
    queryset = Receta.objects.all()
    serializer_class = RecetaSerializer
    
    authentication_classes = [
        authentication.SessionAuthentication, 
        authentication.BasicAuthentication
    ]
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    # --- ACCIONES EXTRA ACTUALIZADAS ---

    @action(detail=True, methods=['get', 'post'], serializer_class=ValoracionSerializer)
    def valorar(self, request, pk=None):
        receta = self.get_object()
        
        # Permitimos GET para que la interfaz no de error 405
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
            return Response({'status': 'Valoración guardada correctamente'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'], serializer_class=FavoritoActionSerializer)
    def favorito(self, request, pk=None):
        receta = self.get_object()
        
        # Permitimos GET para que la interfaz no de error 405
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