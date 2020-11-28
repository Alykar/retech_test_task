from rest_framework import serializers
from .models import *


class OrgCreateSerializer(serializers.ModelSerializer):
    # I need owner to be recorded, for obj.emps management
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.ReadOnlyField()
    tag = serializers.ReadOnlyField()

    class Meta:
        model = Organization
        fields = ('name', 'owner', 'id', 'tag')


class OrgSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    tag = serializers.ReadOnlyField()

    class Meta:
        model = Organization
        fields = ('name', 'tag', 'owner', 'employees')


class UserSerializer(serializers.ModelSerializer):
    snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Organization.objects.all())
    class Meta:
        model = User
        fields = ['id', 'username', 'snippets']


class JoinReqSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = JoinRequest
        fields = ['user', 'org']