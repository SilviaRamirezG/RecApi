from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Receta, Ingrediente, RecetaIngrediente, Comentario, Valoracion, Favorito
from django.db.models import Avg

# --- SERIALIZERS DE USUARIO Y ACCIONES ---

class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class FavoritoActionSerializer(serializers.Serializer):
    es_favorito = serializers.BooleanField(default=True, help_text="Marca para añadir, desmarca para quitar.")

# --- SERIALIZERS DE APOYO (ANIDADOS) ---

class ComentarioSerializer(serializers.ModelSerializer):
    autor = serializers.ReadOnlyField(source='autor.username')

    class Meta:
        model = Comentario
        fields = ['id', 'autor', 'texto', 'fecha_publicacion']

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

# --- SERIALIZER PRINCIPAL DE RECETA ---

class RecetaSerializer(serializers.ModelSerializer):
    # Lectura: Muestra los ingredientes actuales
    ingredientes = RecetaIngredienteSerializer(source='recetaingrediente_set', many=True, read_only=True)
    
    # Escritura: Campo especial para recibir datos tipo JSON al crear/editar
    ingredientes_input = serializers.JSONField(
        write_only=True, 
        required=False, 
        help_text='Formato: [{"nombre": "Tomate", "cantidad": "2 unidades"}]'
    )

    comentarios = ComentarioSerializer(many=True, read_only=True)
    creado_por = serializers.ReadOnlyField(source='creado_por.username')
    total_favoritos = serializers.SerializerMethodField()
    promedio_valoracion = serializers.SerializerMethodField()

    class Meta:
        model = Receta
        fields = [
            'id', 'titulo', 'dificultad', 'tiempo_coccion', 
            'creado_por', 'ingredientes', 'ingredientes_input', 
            'comentarios', 'total_favoritos', 'promedio_valoracion'
        ]

    def get_total_favoritos(self, obj):
        return Favorito.objects.filter(receta=obj).count()

    def get_promedio_valoracion(self, obj):
        promedio = obj.valoraciones.aggregate(Avg('puntuacion'))['puntuacion__avg']
        return promedio if promedio else 0

    def create(self, validated_data):
        # Extraemos los ingredientes antes de crear la receta
        ingredientes_data = validated_data.pop('ingredientes_input', [])
        
        # El usuario se toma del contexto de la solicitud (request)
        receta = Receta.objects.create(creado_por=self.context['request'].user, **validated_data)
        
        # Guardamos los ingredientes vinculándolos a la nueva receta
        for item in ingredientes_data:
            ingrediente_obj, _ = Ingrediente.objects.get_or_create(nombre=item['nombre'])
            RecetaIngrediente.objects.create(
                receta=receta,
                ingrediente=ingrediente_obj,
                cantidad=item['cantidad']
            )
        return receta

    def update(self, instance, validated_data):
        # Extraemos nuevos ingredientes si se enviaron
        ingredientes_data = validated_data.pop('ingredientes_input', None)

        # Actualizamos campos básicos
        instance.titulo = validated_data.get('titulo', instance.titulo)
        instance.dificultad = validated_data.get('dificultad', instance.dificultad)
        instance.tiempo_coccion = validated_data.get('tiempo_coccion', instance.tiempo_coccion)
        instance.save()

        # Si se enviaron nuevos ingredientes, borramos los anteriores y creamos los nuevos
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

