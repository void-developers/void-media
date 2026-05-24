from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from base.models import Posts

class PostsSerializer(ModelSerializer):
    username = serializers.CharField(source='username.username')
    user_id = serializers.IntegerField(source='username.id')
    class Meta:
        model = Posts
        fields = '__all__'