import django_filters # type: ignore
from .models import Comment


class CommentFilter(django_filters.FilterSet):
    post = django_filters.NumberFilter(field_name="post__id")
    author = django_filters.CharFilter(field_name="author__username")

    class Meta:
        model = Comment
        fields = ["post", "author"]
