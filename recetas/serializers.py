from rest_framework import serializers
from .models import Receta, Ingrediente, RecetaIngrediente

class RecetaIngredienteSerializer(serializers.ModelSerializer):
    # Traemos el nombre del ingrediente desde la relación
    nombre = serializers.ReadOnlyField(source='ingrediente.nombre')

    class Meta:
        model = RecetaIngrediente
        fields = ['nombre', 'cantidad']

class RecetaSerializer(serializers.ModelSerializer):
    # Mostramos los ingredientes usando el serializador de la tabla intermedia
    ingredientes = RecetaIngredienteSerializer(source='recetaingrediente_set', many=True, read_only=True)

    class Meta:
        model = Receta
        fields = ['id', 'titulo', 'dificultad', 'ingredientes']

    def create(self, validated_data):
        # Lógica para guardar la receta y sus ingredientes en un solo POST
        ingredientes_data = self.context.get('request').data.get('ingredientes')
        receta = Receta.objects.create(**validated_data)
        
        for item in ingredientes_data:
            ingrediente_obj, _ = Ingrediente.objects.get_or_create(nombre=item['nombre'])
            RecetaIngrediente.objects.create(
                receta=receta,
                ingrediente=ingrediente_obj,
                cantidad=item['cantidad']
            )
        return receta

from rest_framework import serializers
from .models import Receta, Ingrediente, RecetaIngrediente, Comentario, Valoracion, Favorito
from django.contrib.auth.models import User

# Serializador para los comentarios
class ComentarioSerializer(serializers.ModelSerializer):
    autor = serializers.ReadOnlyField(source='autor.username')

    class Meta:
        model = Comentario
        fields = ['id', 'autor', 'texto', 'fecha_publicacion']

# Serializador para la valoración (opcional, si quieres ver quién votó qué)
class ValoracionSerializer(serializers.ModelSerializer):
    autor = serializers.ReadOnlyField(source='autor.username')

    class Meta:
        model = Valoracion
        fields = ['autor', 'puntuacion']

class RecetaIngredienteSerializer(serializers.ModelSerializer):
    nombre = serializers.ReadOnlyField(source='ingrediente.nombre')

    class Meta:
        model = RecetaIngrediente
        fields = ['nombre', 'cantidad']

class RecetaSerializer(serializers.ModelSerializer):
    ingredientes = RecetaIngredienteSerializer(source='recetaingrediente_set', many=True, read_only=True)
    
    # --- NUEVOS CAMPOS AÑADIDOS POR HABER CREADO LAS ESTRUCTURAS (09/03) ---
    comentarios = ComentarioSerializer(many=True, read_only=True)
    creado_por = serializers.ReadOnlyField(source='creado_por.username')
    total_favoritos = serializers.SerializerMethodField()
    promedio_valoracion = serializers.SerializerMethodField()

    class Meta:
        model = Receta
        fields = [
            'id', 'titulo', 'dificultad', 'tiempo_coccion', 
            'creado_por', 'ingredientes', 'comentarios', 
            'total_favoritos', 'promedio_valoracion'
        ]

    def get_total_favoritos(self, obj):
        return Favorito.objects.filter(receta=obj).count()

    def get_promedio_valoracion(self, obj):
        from django.db.models import Avg
        promedio = obj.valoraciones.aggregate(Avg('puntuacion'))['puntuacion__avg']
        return promedio if promedio else 0

    def create(self, validated_data):

        request = self.context.get('request')
        ingredientes_data = request.data.get('ingredientes', [])
        
        # Asignamos el usuario que hace la petición como creador
        receta = Receta.objects.create(creado_por=request.user, **validated_data)
        
        for item in ingredientes_data:
            ingrediente_obj, _ = Ingrediente.objects.get_or_create(nombre=item['nombre'])
            RecetaIngrediente.objects.create(
                receta=receta,
                ingrediente=ingrediente_obj,
                cantidad=item['cantidad']
            )
        return receta

