from SongList.serializers import MusicaSerializer
from rest_framework.views import APIView
from SongList.models import Musica
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import OpenApiTypes

# Create your views here.

# Para retornar uma música específica
class MusicaView(APIView):
    @extend_schema(
        summary="Retorna uma música",
        description="Retorna os dados de uma música específica pelo seu ID.",
        tags=["Músicas"],
        parameters=[
            OpenApiParameter("pk", OpenApiTypes.INT, description="ID da música"),
        ],
        responses={
            200: MusicaSerializer,
            404: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"},
                    },
                    "required": ["detail"],
                },
                description="Não foi encontrada música com o ID fornecido.",
                examples=[
                    OpenApiExample(
                        "Música não encontrada",
                        value={"detail": "Não foi encontrada música com o ID fornecido."},
                        response_only=True,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Exemplo de retorno de música",
                value={
                    "id": 1,
                    "titulo": "Minha música",
                    "artista": "Artista Exemplo",
                    "album": "Álbum Demo",
                    "ano": 2024,
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request, pk):
        """
        Retorna uma música específica em formato JSON.

        Args:
            request: request HTTP enviado pelo cliente.
            pk: ID da música a ser retornada.
        """
        # 'pk' é o mesmo nome que colocamos em urls.py
        try:
            musica = Musica.objects.get(pk=pk)
        except Musica.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = MusicaSerializer(musica)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Atualiza uma música",
        description="Atualiza os dados de uma música existente com base no ID e nos dados fornecidos.",
        tags=["Músicas"],
        request=MusicaSerializer,
        responses={
            200: MusicaSerializer,
            400: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "erro": {"type": "string"},
                    },
                    "required": ["erro"],
                },
                description="Dados inválidos. Verifique os campos e tente novamente.",
                examples=[
                    OpenApiExample(
                        "Dados inválidos",
                        value={"erro": "Dados inválidos. Verifique os campos e tente novamente."},
                        response_only=True,
                    ),
                ],
            ),
            404: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string"},
                    },
                    "required": ["detail"],
                },
                description="Não foi encontrada música com o ID fornecido.",
                examples=[
                    OpenApiExample(
                        "Música não encontrada",
                        value={"detail": "Não foi encontrada música com o ID fornecido."},
                        response_only=True,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Exemplo de atualização de música",
                value={
                    "titulo": "Minha música atualizada",
                    "artista": "Artista Exemplo",
                    "album": "Álbum Atualizado",
                    "ano": 2025,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Exemplo de resposta de atualização",
                value={
                    "id": 1,
                    "titulo": "Minha música atualizada",
                    "artista": "Artista Exemplo",
                    "album": "Álbum Atualizado",
                    "ano": 2025,
                },
                response_only=True,
            ),
        ],
    )
    def put(self, request, pk):
        """
        Atualiza uma música específica.

        Args:
            request: request HTTP contendo os dados a serem atualizados.
            pk: ID da música a ser atualizada.
        """
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
    @extend_schema(
        summary="Lista músicas",
        description="Retorna a lista de todas as músicas cadastradas, ordenadas por título.",
        tags=["Músicas"],
        responses={
            200: MusicaSerializer(many=True),
        },
        examples=[
            OpenApiExample(
                "Exemplo de lista de músicas",
                value=[
                    {
                        "id": 1,
                        "titulo": "Minha música",
                        "artista": "Artista Exemplo",
                        "album": "Álbum Demo",
                        "ano": 2024,
                    },
                    {
                        "id": 2,
                        "titulo": "Outra música",
                        "artista": "Outro Artista",
                        "album": "Outro Álbum",
                        "ano": 2023,
                    },
                ],
                response_only=True,
            ),
        ],
    )
    def get(self, request):
        """
        Lista todas as músicas em formato JSON.

        Args:
            request: request HTTP enviado pelo cliente.
        """
        queryset = Musica.objects.all().order_by('titulo')
        # importante informar que o queryset terá mais
        # de 1 resultado usando many=True
        serializer = MusicaSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Exclui várias músicas",
        description="Exclui as músicas indicadas na lista de IDs fornecida no corpo da requisição.",
        tags=["Músicas"],
        responses={
            204: OpenApiResponse(
                response=None,
                description="Nenhum conteúdo retornado.",
            ),
            404: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"},
                    },
                    "required": ["error"],
                },
                description="Não foi possível encontrar um dos IDs informados.",
                examples=[
                    OpenApiExample(
                        "Música não encontrada",
                        value={"error": "item [ID] não encontrado"},
                        response_only=True,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Exemplo de exclusão",
                value=[1, 2, 3],
                request_only=True,
            ),
        ],
    )
    def delete(self, request):
        """
        Exclui várias músicas pelo ID.

        Args:
            request: request HTTP contendo a lista de IDs a excluir.
        """
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
    @extend_schema(
        summary="Cria uma nova música",
        description="Cria uma nova música no banco de dados a partir dos dados fornecidos no corpo da requisição.",
        tags=["Músicas"],
        request=MusicaSerializer,
        responses={
            201: MusicaSerializer,
            400: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "erro": {"type": "string"},
                    },
                    "required": ["erro"],
                },
                description="Dados inválidos. Verifique os campos e tente novamente.",
                examples=[
                    OpenApiExample(
                        "Dados inválidos",
                        value={"erro": "Dados inválidos. Verifique os campos e tente novamente."},
                        response_only=True,
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Exemplo de criação de música",
                value={
                    "titulo": "Minha música",
                    "artista": "Artista Exemplo",
                    "album": "Álbum Demo",
                    "ano": 2024,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Exemplo de resposta de criação",
                value={
                    "id": 1,
                    "titulo": "Minha música",
                    "artista": "Artista Exemplo",
                    "album": "Álbum Demo",
                    "ano": 2024,
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        """
        Cria uma nova música.

        Args:
            request: request HTTP contendo os dados da nova música.
        """
        serializer = MusicaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

