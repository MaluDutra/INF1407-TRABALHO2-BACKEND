"""Views da API para a aplicação de músicas.

Este módulo implementa endpoints REST para operações de criação, listagem,
consulta, atualização e exclusão de músicas.
"""

from SongList.serializers import MusicaSerializer
from rest_framework.views import APIView
from SongList.models import Musica
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import OpenApiTypes

from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view
from rest_framework_simplejwt.authentication import JWTAuthentication

# Create your views here.

# Para retornar uma música específica e atualizar
class MusicaView(APIView):
    """API view para consultar e atualizar uma música existente.

    GET  /músicas/{pk}/  -> retorna os dados de uma música específica.
    PUT  /músicas/{pk}/  -> atualiza os dados da música indicada pelo ID.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    auth = [{'bearerAuth': []}] # para o Swagger mostrar que é necessário o token JWT

    # Sobrescreve o método get_permissions para permitir que qualquer usuário possa consultar uma música, mas apenas usuários autenticados possam atualizá-la.
    def get_permissions(self):
        if self.request.method == 'PUT':
            return [permission() for permission in [IsAuthenticated]]
        return [permission() for permission in self.permission_classes]

    @extend_schema(
        summary="Retorna uma música",
        description="Retorna os dados de uma música específica pelo seu ID.",
        tags=["Músicas"],
        parameters=[
            OpenApiParameter("pk", OpenApiTypes.INT, description="ID da música"),
        ],
        responses={
            200: MusicaSerializer,
            404: "Não foi encontrada música com o ID fornecido.",
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
            400: "Dados inválidos. Verifique os campos e tente novamente.",
            404: "Não foi encontrada música com o ID fornecido.",
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
    """API view para operações sobre coleções de músicas.

    GET    /músicas/  -> lista todas as músicas.
    DELETE /músicas/  -> exclui múltiplas músicas por ID.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    auth = [{'bearerAuth': []}]  # para o Swagger mostrar que é necessário o token JWT para exclusão

    # Sobrescreve o método get_permissions para permitir que qualquer usuário possa listar músicas, mas apenas usuários autenticados possam excluí-las.
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [permission() for permission in [IsAuthenticated]]
        return [permission() for permission in self.permission_classes]
    
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
        serializer = MusicaSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Exclui várias músicas",
        description="Exclui as músicas indicadas na lista de IDs fornecida no corpo da requisição.",
        tags=["Músicas"],
        responses={
            204: "Nenhum conteúdo retornado.",
            404: "Não foi possível encontrar um dos IDs informados.",
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
    """API view para criar novas músicas.

    POST /músicas/  -> cria uma nova música a partir dos dados fornecidos.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    auth = [{'bearerAuth': []}] # para o Swagger mostrar que é necessário o token JWT
    
    @extend_schema(
        summary="Cria uma nova música",
        description="Cria uma nova música no banco de dados a partir dos dados fornecidos no corpo da requisição.",
        tags=["Músicas"],
        request=MusicaSerializer,
        responses={
            201: MusicaSerializer,
            400: "Dados inválidos. Verifique os campos e tente novamente.",
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

