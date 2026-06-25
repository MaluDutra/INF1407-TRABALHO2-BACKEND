from SongList.serializers import MusicaSerializer
from rest_framework.views import APIView
from SongList.models import Musica
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

# Para retornar uma música específica
class MusicaView(APIView):
    def get(self, request, pk):
        '''
        Retorna uma música específica em formato JSON
        :param self: a própria classe
        :param request: o objeto request (pedido HTTP)
        :param pk: o ID da música a ser retornado
        '''
        # 'pk' é o mesmo nome que colocamos em urls.py
        try:
            musica = Musica.objects.get(pk=pk)
        except Musica.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = MusicaSerializer(musica)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        '''
        Atualiza uma música específica
        :param self: a própria classe
        :param request: o objeto request (pedido HTTP)
        :param pk: o ID da música a ser atualizada
        '''
        try:
            musica = Musica.objects.get(pk=pk)
        except Musica.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = MusicaSerializer(musica, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Para listas as musicas
class MusicasView(APIView):
    def get(self, request):
        queryset = Musica.objects.all().order_by('titulo')
        # importante informar que o queryset terá mais
        # de 1 resultado usando many=True
        serializer = MusicaSerializer(queryset, many=True)
        return Response(serializer.data)

    def delete(self, request):
        id_erro = ""
        erro = False
        for id in request.data:
            musica = Musica.objects.get(id=id)
            if musica:
                musica.delete()
            else:
                id_erro += str(id)
                erro = True
        if erro:
            return Response({'error': f'item [{id_erro}] não encontrado'},status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

# Para criar uma nova música
class MusicaCreateView(APIView):
    def post(self, request):
        serializer = MusicaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

