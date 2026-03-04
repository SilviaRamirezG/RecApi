from django.contrib import admin
from .models import Receta, Ingrediente, RecetaIngrediente

admin.site.register(Receta)
admin.site.register(Ingrediente)
admin.site.register(RecetaIngrediente)
