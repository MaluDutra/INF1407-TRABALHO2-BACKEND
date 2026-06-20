from rest_framework import serializers
from SongList.models import Musica

class MusicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Musica # nome do modelo
        fields = '__all__'  # lista de campos
