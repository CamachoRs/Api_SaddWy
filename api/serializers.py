from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from .models import *

class UsuarioSerializer(serializers.ModelSerializer):
    foto = Base64ImageField(required = False)
    class Meta:
        model = Usuario
        fields = '__all__'

class PreguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pregunta
        fields = '__all__'

class NivelSerializer(serializers.ModelSerializer):
    pregunta_nivel = serializers.SerializerMethodField()
    
    def get_pregunta_nivel(self, obj):
        pregunta = obj.pregunta_nivel.filter(estado=True)
        serializer = PreguntaSerializer(pregunta, many=True)
        return serializer.data
    
    class Meta:
        model = Nivel
        fields = ['id', 'idLenguaje', 'nombre', 'explanation', 'totalPreguntas', 'estado', 'registro', 'pregunta_nivel']
    
class LenguajeSerializer(serializers.ModelSerializer):
    nivel_lenguaje = serializers.SerializerMethodField()
    
    def get_nivel_lenguaje(self, obj):
        nivel = obj.nivel_lenguaje.filter(estado=True)
        serializer = NivelSerializer(nivel, many=True)
        return serializer.data

    class Meta:
        model = Lenguaje
        fields = ['id', 'logo', 'nombre', 'urlDocumentation', 'totalNiveles', 'estado', 'registro', 'nivel_lenguaje']

class ProgresoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progreso
        fields = '__all__'
    
class UsuarioTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioToken
        fields = ['idUsuario', 'token']