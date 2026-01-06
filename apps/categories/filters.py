import django_filters # type: ignore
from .models import Category


class CategoryFilter(django_filters.FilterSet):
    slug = django_filters.CharFilter(field_name="slug")

    class Meta:
        model = Category
        fields = ["slug"]
