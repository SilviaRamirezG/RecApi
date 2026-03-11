from rest_framework import serializers
from .models import Receta, Ingrediente, RecetaIngrediente, Comentario, Valoracion, Favorito
from django.contrib.auth.models import User

# 1. Serializador para los comentarios
class ComentarioSerializer(serializers.ModelSerializer):
    autor = serializers.ReadOnlyField(source='autor.username')

    class Meta:
        model = Comentario
        fields = ['id', 'autor', 'texto', 'fecha_publicacion']

# 2. Serializador para la valoración
class ValoracionSerializer(serializers.ModelSerializer):
    autor = serializers.ReadOnlyField(source='autor.username')

    class Meta:
        model = Valoracion
        fields = ['autor', 'puntuacion']

# 3. Serializador para la tabla intermedia
class RecetaIngredienteSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='ingrediente.nombre')

    class Meta:
        model = RecetaIngrediente
        fields = ['nombre', 'cantidad']

# 4. Serializador Principal de Receta
class RecetaSerializer(serializers.ModelSerializer):
    # Este campo muestra los ingredientes cuando CONSULTAS (GET)
    ingredientes = RecetaIngredienteSerializer(source='recetaingrediente_set', many=True, read_only=True)
    
    # NUEVO: Este campo crea la casilla en el formulario HTML para ESCRIBIR
    # Debes pegar algo como: [{"nombre": "Sal", "cantidad": "1 pizca"}]
    ingredientes_input = serializers.JSONField(write_only=True, required=False, help_text='Formato: [{"nombre": "...", "cantidad": "..."}]')

    comentarios = ComentarioSerializer(many=True, read_only=True)
    creado_por = serializers.ReadOnlyField(source='creado_por.username')
    total_favoritos = serializers.SerializerMethodField()
    promedio_valoracion = serializers.SerializerMethodField()

    class Meta:
        model = Receta
        fields = [
            'id', 'titulo', 'dificultad', 'tiempo_coccion', 
            'creado_por', 'ingredientes', 'ingredientes_input', # Añadimos el input
            'comentarios', 'total_favoritos', 'promedio_valoracion'
        ]

    def get_total_favoritos(self, obj):
        return Favorito.objects.filter(receta=obj).count()

    def get_promedio_valoracion(self, obj):
        from django.db.models import Avg
        promedio = obj.valoraciones.aggregate(Avg('puntuacion'))['puntuacion__avg']
        return promedio if promedio else 0

    def create(self, validated_data):
        # Extraemos los datos del nuevo campo del formulario
        ingredientes_data = validated_data.pop('ingredientes_input', [])
        
        receta = Receta.objects.create(creado_por=self.context['request'].user, **validated_data)
        
        for item in ingredientes_data:
            ingrediente_obj, _ = Ingrediente.objects.get_or_create(nombre=item['nombre'])
            RecetaIngrediente.objects.create(
                receta=receta,
                ingrediente=ingrediente_obj,
                cantidad=item['cantidad']
            )
        return receta

    def update(self, instance, validated_data):
        ingredientes_data = validated_data.pop('ingredientes_input', None)

        instance.titulo = validated_data.get('titulo', instance.titulo)
        instance.dificultad = validated_data.get('dificultad', instance.dificultad)
        instance.tiempo_coccion = validated_data.get('tiempo_coccion', instance.tiempo_coccion)
        instance.save()

        if ingredientes_data is not None:
            RecetaIngrediente.objects.filter(receta=instance).delete()
            for item in ingredientes_data:
                ingrediente_obj, _ = Ingrediente.objects.get_or_create(nombre=item['nombre'])
                RecetaIngrediente.objects.create(
                    receta=instance,
                    ingrediente=ingrediente_obj,
                    cantidad=item['cantidad']
                )

        return instance

