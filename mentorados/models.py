from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
import secrets


# Create your models here.
class Navigators(models.Model):
    nome = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # mentor

    def __str__(self):
        return f"{self.nome}"


class Mentorados(models.Model):
    estado_choices = (("E1", "10-100k"), ("E2", "100-1kk"))
    nome = models.CharField(max_length=255)
    foto = models.ImageField(upload_to="fotos", null=True, blank=True)
    estagio = models.CharField(max_length=2, choices=estado_choices)
    navigator = models.ForeignKey(Navigators, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # mentor
    criado_em = models.DateField(auto_now_add=True)
    token = models.CharField(max_length=16)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.gerar_token_unico()
        super().save(*args, **kwargs)

    def gerar_token_unico(self):
        while True:
            token = secrets.token_urlsafe(8)
            if not Mentorados.objects.filter(token=token).exists():
                return token

    def __str__(self):
        return f"{self.nome}"


class DisponibilidadedeHorarios(models.Model):
    data_inicial = models.DateTimeField(null=True, blank=True)
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    agendado = models.BooleanField(default=False)

    def data_final(self):
        return self.data_inicial + timedelta(minutes=50)
