"""Modelos para gerenciamento de redefinição de senha.

Este módulo define a entidade `PasswordResetCode`, que registra um código de
redefinição de senha gerado para um usuário e controla seu uso e validade.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class PasswordResetCode(models.Model):
    """Código de redefinição de senha vinculado a um usuário.

    Cada instância representa um token de redefinição enviado por e-mail, que
    pode ser usado uma única vez dentro do período de validade.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    
    def __str__(self):
        """Retorna uma representação legível do código de redefinição."""
        return f"{self.user.email} - {self.code}"
    
    def is_expired(self):
        """Retorna True se o código de redefinição estiver expirado."""
        # Considera o código expirado após 15 minutos
        return timezone.now() > self.created_at + timezone.timedelta(minutes=15)
