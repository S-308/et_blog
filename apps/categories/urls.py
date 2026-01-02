from django.urls import path
from .views import (
    CategoryListAPIView,
    CategoryDetailAPIView,
    CategoryCreateAPIView,
    CategoryUpdateDeleteAPIView,
)

urlpatterns = [
    path("categories/", CategoryListAPIView.as_view()),
    path("categories/<slug:slug>/", CategoryDetailAPIView.as_view()),
    path("categories/create/", CategoryCreateAPIView.as_view()),
    path("categories/<slug:slug>/manage/", CategoryUpdateDeleteAPIView.as_view()),
]
