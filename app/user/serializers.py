from django.contrib.auth import get_user_model
# from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    '''user object serializer'''

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        '''user 생성 및 비밀번호 암호화'''
        user = get_user_model().objects.create_user(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        '''user 업데이트'''
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user