"""Views de gerenciamento de autenticação e recuperação de senha.

Este módulo expõe endpoints para:
- consultar o usuário autenticado;
- alterar a senha do usuário autenticado;
- solicitar redefinição de senha via token;
- confirmar a redefinição de senha.
"""

import secrets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

from gerenciamento.models import PasswordResetCode
from gerenciamento.serializers import ChangePasswordSerializer
from gerenciamento.serializers import ResetPasswordRequestSerializer
from gerenciamento.serializers import ResetPasswordConfirmSerializer
from gerenciamento.serializers import RegisterSerializer

from rest_framework import status
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import extend_schema
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

# Create your views here.

@api_view(['GET'])
def whoami(request):
    '''
    Retorna os dados do usuário autenticado.
    Esta função só deve ser chamada quando o usuário já estiver
    autenticado, e devolve apenas informações básicas de identificação.
    '''
    dados = {
        'id': request.user.id,
        'username': request.user.username,
    }
    return Response(dados)

class ChangePasswordView(APIView):
    """Endpoint para alteração de senha do usuário autenticado.

    O usuário deve estar autenticado para atualizar sua própria senha.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Alterar senha do usuário autenticado",
        description="Permite que o usuário autenticado altere sua senha fornecendo a senha antiga e a nova senha.",
        tags=["gerenciamento"],
        request=ChangePasswordSerializer,
        responses={
            200: "Senha alterada com sucesso",
            400: "Erro na alteração da senha"
        },
        examples=[
            OpenApiExample(
                "Exemplo de requisição para alterar senha",
                value={
                    "old_password": "S3736-1001!",
                    "new_password": "S12345678!"
                }
            ),
        ],
    )
    def put(self, request):
        '''
        Permite que o usuário autenticado altere sua senha.

        A requisição deve conter os campos 'old_password' e 'new_password'.
        Se a senha antiga estiver correta, a nova senha é salva no usuário.
        '''
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'error': 'Senha antiga incorreta'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'status': 'Senha alterada com sucesso'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """Endpoint para fluxo de recuperação de senha.

    A view permite solicitar um token de redefinição por e-mail e confirmar
    a redefinição utilizando este token.
    """

    authentication_classes = [] # Desabilita autenticação para esta view
    permission_classes = [AllowAny] # Permite acesso sem autenticação

    @extend_schema(
        summary="Solicitar redefinição de senha",
        description="Permite que um usuário solicite um código de redefinição de senha fornecendo seu e-mail.",
        tags=["gerenciamento"],
        request=ResetPasswordRequestSerializer,
        responses={
            200: "E-mail de redefinição de senha enviado com sucesso",
            404: "Nenhum usuário encontrado com este e-mail"
        },
        examples=[
            OpenApiExample(
                "Exemplo de requisição para solicitar redefinição de senha",
                value={ "email": "usuario@exemplo.com" }
            )
        ],
    )
    def post(self, request):
        '''
        Lida com a solicitação de redefinição de senha.

        Recebe um e-mail e, se o usuário existir, gera um código de reset
        que é enviado por e-mail ao usuário. O token também é retornado
        no corpo da resposta para fins de desenvolvimento/teste.
        '''
        serializer = ResetPasswordRequestSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # A mensagem deveria ser genérica para não revelar se o e-mail existe ou não,
                # mas para fins de teste e desenvolvimento, vamos retornar um erro específico.
                # Por exemplo: "Se o email existir, enviaremos o código"
                return Response({'message': 'Nenhum usuário encontrado com este e-mail'}, status=status.HTTP_404_NOT_FOUND)
            
            # Cria código de redefinição de senha e salva no banco de dados
            code = secrets.token_urlsafe(16)
            PasswordResetCode.objects.create(user=user, code=code)
            # send an e-mail to the user
            context = {
                'current_user': user.first_name + ' ' + user.last_name if user.last_name else user.first_name,
                'username': user.username,
                'email': user.email,
                'token': code,
            }

            # render email text
            email_html_message = render_to_string('email/password_reset_email.html', context)
            email_plaintext_message = render_to_string('email/password_reset_email.txt', context)

            msg = EmailMultiAlternatives(
                "Redefinição de senha para o site de Exemplos Web", # title:
                email_plaintext_message, # arquivo com mensagem texto ou None para apenas HTML
                "noreply@yourdomain.com", # from:
                [user.email] # to:
            )

            msg.attach_alternative(email_html_message, "text/html")
            msg.send()
        return Response({
                'message': 'E-mail de redefinição de senha enviado com sucesso',
                'token': str(code)
            },
            status=status.HTTP_200_OK
        )

    
    @extend_schema(
        summary="Confirmar redefinição de senha",
        description="Permite que um usuário confirme a redefinição de senha fornecendo um código de redefinição e a nova senha.",
        tags=["accounts"],
        request=ResetPasswordConfirmSerializer,
        responses={
            200: "Senha redefinida com sucesso",
            400: "Código de redefinição inválido ou expirado"
        },
        examples=[
            OpenApiExample(
                "Exemplo de requisição para confirmar redefinição de senha",
                value={
                    "code": "código-de-redefinição-aqui",
                    "new_password": "S12345678!"
                },
            ),
        ],
    )
    def put(self, request):
        '''
        Lida com a confirmação da redefinição de senha.

        Recebe o código de redefinição e a nova senha. Se o código existir,
        não estiver expirado e ainda não tiver sido utilizado, a senha do
        usuário é atualizada e o código é marcado como usado.
        '''
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['new_password']
            try:
                reset_code = PasswordResetCode.objects.get(code=code, used=False)
            except PasswordResetCode.DoesNotExist:
                return Response({'error': 'Código de redefinição inválido ou já utilizado'}, status=status.HTTP_400_BAD_REQUEST)

            if reset_code.is_expired():
                return Response({'error': 'Código de redefinição expirado'}, status=status.HTTP_400_BAD_REQUEST)

            user = reset_code.user
            user.set_password(new_password)
            user.save()
            reset_code.used = True
            reset_code.save()
            return Response({'status': 'Senha redefinida com sucesso'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RegisterView(APIView):
    """Endpoint para cadastro de novos usuários."""

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Cadastrar novo usuário",
        description="Cria um usuário novo a partir de username, e-mail e senha.",
        tags=["gerenciamento"],
        request=RegisterSerializer,
        responses={
            201: "Usuário criado com sucesso",
            400: "Dados inválidos ou usuário já existe",
        },
        examples=[
            OpenApiExample(
                "Exemplo de requisição para cadastro",
                value={
                    "username": "usuario123",
                    "email": "usuario@exemplo.com",
                    "password": "SenhaForte123!",
                    "password_confirm": "SenhaForte123!",
                },
            ),
        ],
    )
    def post(self, request):
        '''
        Cria um novo usuário no sistema.

        Recebe username, email, password e password_confirm no corpo da requisição.
        '''
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
