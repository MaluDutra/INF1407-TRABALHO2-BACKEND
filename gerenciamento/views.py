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
    '''
    dados = {
        'id': request.user.id,
        'username': request.user.username,
    }
    return Response(dados)

class ChangePasswordView(APIView):
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
        Espera receber a senha antiga em 'old_password'
        e a nova senha em 'new_password' no corpo da requisição.
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
        Espera receber um e-mail no corpo da requisição para identificar o usuário.
        Gera um token de redefinição de senha e envia um e-mail para o usuário com instruções.
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
    
