from django.db.models.signals import post_save
from django.dispatch import receiver
from Usuarios.models import Usuario
from .models import Carrito

@receiver(post_save, sender=Usuario)
def create_carrito(sender, instance, created, **kwargs):
    if created:
        Carrito.objects.create(usuario=instance)