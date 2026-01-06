import django_filters # type: ignore
from .models import Tag


class TagFilter(django_filters.FilterSet):
    slug = django_filters.CharFilter(field_name="slug")

    class Meta:
        model = Tag
        fields = ["slug"]
