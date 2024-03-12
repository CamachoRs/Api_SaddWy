from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save
from .models import *
import hashlib, random

@receiver(post_save, sender=Nivel)
@receiver(post_delete, sender=Nivel)
def actualizar_total_preguntas(sender, instance, **kwargs):
    lenguaje = instance.idLenguaje
    lenguaje.totalNiveles = Nivel.objects.filter(idLenguaje = lenguaje, estado = True).count()
    lenguaje.save()

@receiver(post_save, sender = Pregunta)
@receiver(post_delete, sender = Pregunta)
def totalPReguntasNivel(sender, instance, **kwargs):
    nivel = instance.idNivel
    nivel.totalPreguntas = Pregunta.objects.filter(idNivel = nivel, estado = True).count()
    nivel.save()

@receiver(pre_save, sender = Progreso)
def actualizarProgresoLenguaje(sender, instance, **kwargs):
    cantidad_total = Nivel.objects.filter(idLenguaje=instance.idLenguaje, estado=True).count()
    cantidad_realizada = len(instance.historial)
    
    if cantidad_total > 0:
        instance.progresoLenguaje = (100 * cantidad_realizada) / cantidad_total
    
@receiver(post_save, sender = Usuario)
def verificarUsuario(sender, instance, created, **kwargs):
    if created:
        id_foto = random.randint(1, FotoUsuario.objects.count())
        instance.foto = FotoUsuario.objects.get(id = id_foto).foto
        instance.save()
        bytes = str(instance.id).encode('utf-8')
        hashed = hashlib.sha256(bytes).hexdigest()
        UsuarioToken.objects.create(idUsuario = instance, token = hashed)