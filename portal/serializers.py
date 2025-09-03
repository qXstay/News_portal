from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.user.username')

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'content',
            'created_at',
            'author',
            'post_type',
            'categories'
        ]
        read_only_fields = ['created_at', 'author', 'post_type']