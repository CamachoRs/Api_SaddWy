from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()
router.register(r'usuario', UsuarioView)
router.register(r'lenguaje', LenguajeView)
router.register(r'progreso', ProgresoView)

urlpatterns = [
    path('v01/', include(router.urls)),
    path('v01/ingresar/', Log_in),
    path('v01/validar/', validarUsuario),
]