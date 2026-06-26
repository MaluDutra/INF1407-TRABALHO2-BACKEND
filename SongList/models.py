"""Modelos de dados para o aplicativo de lista de músicas.

Este módulo define a classe de modelo `Musica`, que representa uma música
armazenada no banco de dados.
"""

from django.db import models
from django.contrib.auth.models import User


class Musica(models.Model):
    """Representa uma música com título, artista, álbum e ano de lançamento.

    O campo `criador` mantém a referência ao usuário que adicionou a música.
    Quando o usuário é removido, o campo fica como NULL (a música permanece
    no acervo, mas sem dono — comportando-se como pública).
    Para as músicas pré-existentes (carregadas pelo comando ``populate_songs``),
    `criador` também fica NULL, e elas não podem ser editadas/removidas por
    nenhum usuário comum, apenas visualizadas.
    """
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200, db_column='TITULO')
    artista = models.CharField(max_length=200, db_column='ARTISTA')
    album = models.CharField(max_length=200, blank=True, null=True, db_column='ALBUM')
    ano = models.IntegerField(blank=True, null=True, db_column='ANO')
    criador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='musicas',
        db_column='CRIADOR_ID',
    )

    class Meta:
        managed = True
        db_table = 'Musicas'
        ordering = ['titulo']

    def __str__(self):
        """Retorna uma representação legível da música."""
        return f"{self.titulo} - {self.artista}"
        