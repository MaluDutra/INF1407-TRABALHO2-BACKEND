from django.db import models

class Musica(models.Model):
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
        return f"{self.titulo} - {self.artista}"
