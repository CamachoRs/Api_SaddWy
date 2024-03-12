from django.contrib import admin
from .models import *

# Register your models here
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'foto', 'nombre', 'correo', 'password', 'estado', 'registro']

class LenguajeAdmin(admin.ModelAdmin):
    list_display = ['id', 'logo', 'nombre', 'urlDocumentation', 'totalNiveles', 'estado', 'registro']

class NivelAdmin(admin.ModelAdmin):
    list_display = ['id', 'idLenguaje', 'nombre', 'explanation', 'totalPreguntas', 'estado', 'registro']

class PreguntaAdmin(admin.ModelAdmin):
    list_display = ['id', 'idNivel', 'tipoPregunta', 'explanation', 'pregunta', 'respuesta', 'estado', 'registro']

class ProgresoAdmin(admin.ModelAdmin):
    list_display = ['id', 'idUsuario', 'idLenguaje', 'progresoLenguaje', 'historial', 'puntos', 'registro']

class UsuarioTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'idUsuario', 'token', 'registro']

class FotoUsuarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'foto']

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Lenguaje, LenguajeAdmin)
admin.site.register(Nivel, NivelAdmin)
admin.site.register(Pregunta, PreguntaAdmin)
admin.site.register(Progreso, ProgresoAdmin)
admin.site.register(UsuarioToken, UsuarioTokenAdmin)
admin.site.register(FotoUsuario, FotoUsuarioAdmin)