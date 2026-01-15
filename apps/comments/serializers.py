from rest_framework import serializers
from .models import Comment
from drf_spectacular.utils import extend_schema_field


class RecursiveCommentSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = CommentListSerializer(value, context=self.context)
        return serializer.data


class CommentListSerializer(serializers.ModelSerializer):
    replies = RecursiveCommentSerializer(many=True, read_only=True)
    reply_count = serializers.SerializerMethodField()
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "content",
            "author",
            "created_at",
            "reply_count",
            "replies",
        )

    @extend_schema_field(int)
    def get_reply_count(self, obj):
        # Use prefetched replies if available
        if hasattr(obj, "_prefetched_objects_cache") and "replies" in obj._prefetched_objects_cache:
            return len(obj.replies.all())
        return obj.replies.count()


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content", "parent"]

    def validate_parent(self, parent):
        if parent is None:
            return None

        post = self.context.get("post")
        if post is not None and parent.post_id != post.id:
            raise serializers.ValidationError(
                "You cannot reply to a comment from another post."
            )

        max_depth = 3
        depth = 1
        current = parent
        while current.parent_id:
            depth += 1
            current = current.parent

        if depth >= max_depth:
            raise serializers.ValidationError(
                "Maximum comment nesting depth reached."
            )

        return parent


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

