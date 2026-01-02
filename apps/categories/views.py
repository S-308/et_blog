from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import Category
from .serializers import CategoryListSerializer
from rest_framework.permissions import IsAdminUser
from .serializers import CategoryCreateUpdateSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter


class CategoryListAPIView(APIView):
    """
    GET (Public)
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="List categories",
        description="Public endpoint to list all categories.",
        responses=CategoryListSerializer(many=True),
    )

    def get(self, request):
        categories = Category.objects.all().order_by("id")
        serializer = CategoryListSerializer(categories, many=True)
        return Response(serializer.data)
    

class CategoryDetailAPIView(APIView):
    """
    GET (Public)
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Retrieve category",
        description="Retrieve a category by its slug.",
        parameters=[
            OpenApiParameter(
                name="slug",
                description="Category slug",
                required=True,
                type=str,
                location=OpenApiParameter.PATH,
            )
        ],
        responses=CategoryListSerializer,
    )

    def get(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return Response(
                {"detail": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CategoryListSerializer(category)
        return Response(serializer.data)

class CategoryCreateAPIView(APIView):
    """
    POST (Admin only)
    """

    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Create category",
        description="Admin-only endpoint to create a new category.",
        request=CategoryCreateUpdateSerializer,
        responses=CategoryListSerializer,
    )

    def post(self, request):
        serializer = CategoryCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        category = serializer.save(
            created_by=request.user
        )

        return Response(
            CategoryListSerializer(category).data,
            status=status.HTTP_201_CREATED
        )

class CategoryUpdateDeleteAPIView(APIView):
    """
    PATCH  (Admin)
    DELETE (Admin)
    """

    permission_classes = [IsAdminUser]

    def get_object(self, slug):
        try:
            return Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return None

    @extend_schema(
        summary="Update category",
        description="Admin-only endpoint to update a category.",
        parameters=[
            OpenApiParameter(
                name="slug",
                description="Category slug",
                required=True,
                type=str,
                location=OpenApiParameter.PATH,
            )
        ],
        request=CategoryCreateUpdateSerializer,
        responses=CategoryListSerializer,
    )

    def patch(self, request, slug):
        category = self.get_object(slug)
        if not category:
            return Response(
                {"detail": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CategoryCreateUpdateSerializer(
            category,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        category = serializer.save()
        category.updated_by = request.user
        category.save(update_fields=["updated_by"])

        return Response(CategoryListSerializer(category).data)

    @extend_schema(
        summary="Delete category",
        description="Admin-only endpoint to delete a category.",
        parameters=[
            OpenApiParameter(
                name="slug",
                description="Category slug",
                required=True,
                type=str,
                location=OpenApiParameter.PATH,
            )
        ],
    )

    def delete(self, request, slug):
        category = self.get_object(slug)
        if not category:
            return Response(
                {"detail": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
