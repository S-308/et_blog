from rest_framework import serializers
from .models import Post
from apps.categories.models import Category
from apps.tags.models import Tag


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "slug",
            "author",
            "category",
            "tags",
            "status",
            "created_at",
        )


class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = Post
        fields = "__all__"
        read_only_fields = (
            "id",
            "author",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )



class PostCreateUpdateSerializer(serializers.ModelSerializer):

    category = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    tags = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Tag.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Post
        fields = (
            "title",
            "content",
            "status",
            "category",
            "tags",
        )

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if request:
            instance.updated_by = request.user

        return super().update(instance, validated_data)
