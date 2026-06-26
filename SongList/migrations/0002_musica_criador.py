"""Migration que adiciona o campo `criador` à tabela de músicas.

O campo é uma chave estrangeira para o modelo de usuário do Django.
Permite que cada música tenha um dono, usado para autorizar edição e
remoção apenas pelo próprio criador.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("SongList", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="musica",
            name="criador",
            field=models.ForeignKey(
                blank=True,
                db_column="CRIADOR_ID",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="musicas",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
    