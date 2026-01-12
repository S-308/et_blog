from rest_framework import serializers
from .models import Comment



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

    def get_reply_count(self, obj):
        return obj.replies.filter(is_deleted=False).count()


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content", "parent"]

        def validate_parent(self, parent):
            if parent:
                post = self.context.get("post")
                if parent.post != post:
                    raise serializers.ValidationError(
                        "You cannot reply to a comment from another post."
                    )

            depth = 1
            current = parent
            while current.parent:
                depth += 1
                current = current.parent

            if depth >= 3:
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

