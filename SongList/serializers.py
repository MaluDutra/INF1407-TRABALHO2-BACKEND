"""Serializadores para a API de músicas.

Este módulo define a forma como as instâncias de `Musica` são convertidas
para e a partir de JSON na API REST.
"""

from rest_framework import serializers
from SongList.models import Musica


class MusicaSerializer(serializers.ModelSerializer):
    """Serializador para o modelo `Musica`.

    Usa o `ModelSerializer` do Django REST Framework para mapear todos os
    campos do modelo `Musica` automaticamente. O campo `criador` é apenas
    de leitura — quem grava esse valor é a view, no momento da criação,
    a partir do usuário autenticado da requisição.
    """

    class Meta:
        model = Musica
        fields = '__all__'
        read_only_fields = ['criador']

        