from rest_framework import serializers
from rest_framework.authtoken.models import Token

from core.users.models import HospitalUser

class HospitalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalUser
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(allow_null=False)
    password = serializers.CharField(allow_null=False)

class WorkScheduleSerializer(serializers.Serializer):
    start_time = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", input_formats=["%d-%m-%Y %H:%M:%S", ], required=True, allow_null=False)
    end_time = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", input_formats=["%d-%m-%Y %H:%M:%S", ], allow_null=False)

class UserTokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source='key')
    user = HospitalUserSerializer()
    class Meta:
        model = Token
        fields = ('token', 'user')

    def to_representation(self, instance):
        data = super(UserTokenSerializer, self).to_representation(instance)
        user = data.get('user')
        user.update({
            'token': data.get('token'),
        })

        return user