from django.db import models

# Create your models here.
class Usuario(models.Model):
    foto = models.ImageField(upload_to = 'usuario/')
    nombre = models.CharField(max_length = 50)
    correo = models.EmailField(unique = True)
    password = models.CharField(max_length = 100)
    estado = models.BooleanField(default = False)
    registro = models.DateField(auto_now_add = True)

class Lenguaje(models.Model):
    logo = models.ImageField(upload_to = 'lenguajes/')
    nombre = models.CharField(max_length = 50, unique = True)
    urlDocumentation = models.URLField(max_length = 2083)
    totalNiveles = models.PositiveIntegerField(default = 0)
    estado = models.BooleanField(default = False)
    registro = models.DateField(auto_now_add = True)

class Nivel(models.Model):
    idLenguaje = models.ForeignKey(Lenguaje, on_delete = models.CASCADE, related_name = 'nivel_lenguaje', limit_choices_to={'estado': True})
    nombre = models.CharField(max_length = 50)
    explanation = models.TextField()
    totalPreguntas = models.PositiveIntegerField(default = 0)
    estado = models.BooleanField(default = False)
    registro = models.DateField(auto_now_add = True)

class Pregunta(models.Model):
    idNivel = models.ForeignKey(Nivel, on_delete = models.CASCADE, related_name = 'pregunta_nivel', limit_choices_to = {'estado': True})
    tipoPregunta = models.CharField(max_length = 20, choices = [
        ['opcion_multiple', 'Pregunta de opción múltiple'],
        ['verdadero_falso', 'Pregunta de verdadero y falso'],
        ['respuesta_abierta', 'Pregunta de respuesta abierta'],
    ])
    explanation = models.TextField()
    pregunta = models.TextField()
    respuesta = models.JSONField()
    estado = models.BooleanField(default = False)
    registro = models.DateField(auto_now_add = True)

class Progreso(models.Model):
    idUsuario = models.ForeignKey(Usuario, on_delete = models.CASCADE, limit_choices_to = {'estado': True})
    idLenguaje = models.ForeignKey(Lenguaje, on_delete = models.CASCADE, limit_choices_to = {'estado': True})
    progresoLenguaje = models.FloatField(default = 0)
    historial = models.JSONField()
    puntos = models.PositiveIntegerField(default = 0)
    registro = models.DateField(auto_now_add = True)

class UsuarioToken(models.Model):
    idUsuario = models.ForeignKey(Usuario, on_delete = models.CASCADE, limit_choices_to = {'estado': True})
    token = models.CharField(max_length = 100)
    registro = models.DateTimeField(auto_now_add = True)

class FotoUsuario(models.Model):
    foto = models.ImageField(upload_to = 'predeterminados/')