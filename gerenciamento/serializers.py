"""Serializadores para o gerenciamento de senhas.

Este módulo define os serializers usados pelas views de alteração de senha
e de recuperação de senha no aplicativo de gerenciamento.
"""

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
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


class RegisterSerializer(serializers.Serializer):
    '''
    Serializer para cadastro de novo usuário.
    '''
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=8)
    password_confirm = serializers.CharField(required=True, write_only=True, min_length=8)

    def validate(self, data):
        '''
        Valida se as duas senhas coincidem.
        '''
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'As senhas não coincidem.'})
        return data

    def validate_password(self, value):
        '''
        Valida a senha usando os validadores do Django.
        '''
        validate_password(value)
        return value

    def create(self, validated_data):
        '''
        Cria um novo usuário no banco de dados.
        '''
        validated_data.pop('password_confirm', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user

