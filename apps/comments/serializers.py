from rest_framework import serializers
from .models import Comment

class CommentListSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "content",
            "created_at",
        )

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("content",)

class CommentDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = (
            "id",
            "post",
            "author",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )
