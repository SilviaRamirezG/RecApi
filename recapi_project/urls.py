"""
URL configuration for recapi_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include 
from rest_framework.routers import DefaultRouter
from recetas.views import RecetaViewSet 

router = DefaultRouter()
router.register(r'recetas', RecetaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Ruta para tus recetas (http://127.0.0.1:8000/api/recetas/)
    path('api/', include(router.urls)),
    
    # Para loguear (http://127.0.0.1:8000/api-auth/login/)
    path('api-auth/', include('rest_framework.urls')),
]
