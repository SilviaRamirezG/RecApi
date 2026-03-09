from django.db import models
from django.contrib.auth.models import User

# Catálogo Maestro de Ingredientes
class Ingrediente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

# Modelo de Recetas
class Receta(models.Model):
    
    DIFICULTAD_CHOICES = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
    ]
    
    titulo = models.CharField(max_length=200)
    tiempo_coccion = models.PositiveIntegerField(help_text="Tiempo en minutos")
    dificultad = models.CharField(max_length=10, choices=DIFICULTAD_CHOICES)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    # Muchos-a-Muchos (N:M)
    # Se utiliza 'through' para la tabla intermedia
    ingredientes = models.ManyToManyField(Ingrediente, through='RecetaIngrediente')

    def __str__(self):
        return self.titulo

# Receta_Ingredientes (para el campo 'cantidad')
class RecetaIngrediente(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad = models.CharField(max_length=100, help_text="Ej: 200g o 2 cucharadas")

    def __str__(self):
        return f"{self.receta} - {self.ingrediente}"
# Pasos de Preparación
class PasoPreparacion(models.Model):
    receta = models.ForeignKey(Receta, related_name='pasos', on_delete=models.CASCADE)
    orden = models.PositiveIntegerField()
    descripcion = models.TextField()

    class Meta:
        ordering = ['orden']

# --- Modelos nuevos incorporados que no estan en el PDF (09/03) ---

class Comentario(models.Model):
    receta = models.ForeignKey(Receta, related_name='comentarios', on_delete=models.CASCADE)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.autor} en {self.receta}"

class Valoracion(models.Model):
    receta = models.ForeignKey(Receta, related_name='valoraciones', on_delete=models.CASCADE)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    puntuacion = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)]) # Valoración de 1 a 5 estrellas

    class Meta:
        unique_together = ('receta', 'autor') # Evita que un usuario valore dos veces la misma receta

class Favorito(models.Model):
    user = models.ForeignKey(User, related_name='mis_favoritos', on_delete=models.CASCADE)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'receta') # Hace que no puedas repetir favoritos