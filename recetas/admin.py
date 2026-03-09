from django.contrib import admin
from .models import Receta, Ingrediente, RecetaIngrediente, Comentario, Valoracion, Favorito

admin.site.register(Receta)
admin.site.register(Ingrediente)
admin.site.register(RecetaIngrediente)
admin.site.register(Comentario)
admin.site.register(Valoracion)
admin.site.register(Favorito)