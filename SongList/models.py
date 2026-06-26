"""Modelos de dados para o aplicativo de lista de músicas.

Este módulo define a classe de modelo `Musica`, que representa uma música
armazenada no banco de dados.
"""

from django.db import models

class Musica(models.Model):
    """Representa uma música com título, artista, álbum e ano de lançamento."""
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200, db_column='TITULO')
    artista = models.CharField(max_length=200, db_column='ARTISTA')
    album = models.CharField(max_length=200, blank=True, null=True, db_column='ALBUM')
    ano = models.IntegerField(blank=True, null=True, db_column='ANO')

    class Meta:
        managed = True
        db_table = 'Musicas'
        ordering = ['titulo']

    def __str__(self):
        """Retorna uma representação legível da música."""
        return f"{self.titulo} - {self.artista}"
