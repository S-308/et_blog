from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import Category
from .serializers import CategoryListSerializer
from rest_framework.permissions import IsAdminUser
from .serializers import CategoryCreateUpdateSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework.pagination import PageNumberPagination
from .filters import CategoryFilter


class CategoryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class CategoryListAPIView(APIView):
    """
    GET (Public)
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="List categories",
        description=(
            "Retrieve a paginated list of categories. "
            "This endpoint is public and supports filtering."
        ),
        parameters=[
            OpenApiParameter("page", int, description="Page number"),
            OpenApiParameter("page_size", int, description="Number of items per page"),
        ],
        responses={
            200: CategoryListSerializer(many=True),
        },
    )

    def get(self, request):
        categories = Category.objects.order_by("id")    # .filter(is_deleted=False)
    
        filterset = CategoryFilter(request.GET, queryset=categories)
        queryset = filterset.qs

        paginator = CategoryPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = CategoryListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)
    

class CategoryDetailAPIView(APIView):
    """
    GET (Public)
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Retrieve category",
        description="Retrieve a single category by its slug.",
        parameters=[
            OpenApiParameter(
                name="slug",
                description="Category slug",
                required=True,
                type=str,
                location=OpenApiParameter.PATH,
            )
        ],
        responses={
            200: CategoryListSerializer,
            404: OpenApiResponse(description="Category not found"),
        },
    )

    def get(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return Response(
                {"detail": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        # get_object_or_404(Category.objects, slug=slug)
        serializer = CategoryListSerializer(category)
        return Response(serializer.data)

class CategoryCreateAPIView(APIView):
    """
    POST (Admin only)
    """

    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Create category",
        description=(
            "Create a new category. "
            "This endpoint is restricted to admin users."
        ),
        request=CategoryCreateUpdateSerializer,
        responses={
            201: CategoryListSerializer,
            400: OpenApiResponse(description="Invalid data or creation failed"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin privileges required"),
        },
    )

    def post(self, request):
        serializer = CategoryCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            category = serializer.save(created_by=request.user)
        except Exception:
            return Response(
                {"detail": "Category creation failed"},
                status=status.HTTP_400_BAD_REQUEST,
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
        description=(
            "Update an existing category. "
            "This endpoint is restricted to admin users."
        ),
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
        responses={
            200: CategoryListSerializer,
            400: OpenApiResponse(description="Invalid data"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin privileges required"),
            404: OpenApiResponse(description="Category not found"),
        },
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
        description=(
            "Delete a category. "
            "This operation is idempotent and restricted to admin users."
        ),
        parameters=[
            OpenApiParameter(
                name="slug",
                description="Category slug",
                required=True,
                type=str,
                location=OpenApiParameter.PATH,
            )
        ],
        responses={
            204: OpenApiResponse(description="Category deleted successfully"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin privileges required"),
            404: OpenApiResponse(description="Category not found"),
        },
    )

    def delete(self, request, slug):
        category = self.get_object(slug)
        if not category:
            return Response(
                {"detail": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        # GUARD: idempotent delete
        if category.is_deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)

        category.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
