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