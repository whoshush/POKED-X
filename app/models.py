from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save # Para crear el perfil automáticamente
from django.dispatch import receiver # Para conectar la señal
from datetime import datetime, timedelta # Para manejar fechas y tiempos

class Favourite(models.Model):
    # Detalles del pokemon.
    id = models.IntegerField(primary_key=True, blank=True) #ID de pokeapi
    name = models.CharField(max_length=200)  # Nombre del personaje
    height = models.CharField(max_length=200)  # Altura
    weight = models.CharField(max_length=200)  # Peso
    base_experience = models.IntegerField(null=True, blank=True)  # Experiencia base
    types = models.JSONField(default=list)  # Lista de tipos (ej: ["grass", "poison"])
    image = models.URLField()  # URL de la imagen

    # Asociamos el favorito con el usuario que lo guarda.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        # Restringe duplicados: un mismo usuario no puede guardar el mismo personaje varias veces.
        unique_together = (('user', 'name'),)

    def __str__(self):
        return (f"{self.name} - Altura: {self.height if self.height else 'Desconocida'} "
                f"(Peso: {self.weight if self.weight else 'Desconocido'}) - "
                f"User: {self.user.username}")
        


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    failed_login_attempts = models.IntegerField(default=0)
    lockout_until = models.DateTimeField(null=True, blank=True) # Cuándo se desbloquea la cuenta

    def __str__(self):
        return self.user.username

# Señales para crear/guardar UserProfile automáticamente cuando se crea/guarda un User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
