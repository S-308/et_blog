import django_filters # type: ignore
from .models import Post


class PostFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category__slug")
    tag = django_filters.CharFilter(field_name="tags__slug")
    author = django_filters.CharFilter(field_name="author__username")
    status = django_filters.CharFilter(field_name="status")

    class Meta:
        model = Post
        fields = ["category", "tag", "author", "status"]
