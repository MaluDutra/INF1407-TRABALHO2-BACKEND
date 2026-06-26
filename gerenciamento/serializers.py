"""Serializadores para o gerenciamento de senhas.

Este módulo define os serializers usados pelas views de alteração de senha
e de recuperação de senha no aplicativo de gerenciamento.
"""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

class ChangePasswordSerializer(serializers.Serializer):
    '''
    Serializer para a alteração de senha do usuário autenticado.
    '''
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        '''
        Valida a nova senha usando os validadores de senha do Django.
        '''
        validate_password(value)
        return value

class ResetPasswordRequestSerializer(serializers.Serializer):
    '''
    Serializer para a solicitação de redefinição de senha.
    '''
    email = serializers.EmailField(required=True)


class ResetPasswordConfirmSerializer(serializers.Serializer):
    '''
    Serializer para confirmação da redefinição de senha.
    '''
    code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    
    def validate_new_password(self, value):
        '''
        Valida a nova senha usando os validadores de senha do Django.
        '''
        validate_password(value)
        return value

