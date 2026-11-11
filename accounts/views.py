import json

from django.http import JsonResponse, HttpResponse
from django.views import View
from django.contrib.auth import get_user_model
from django.db.models import Prefetch

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAdminUser
from dj_rest_auth.views import PasswordResetConfirmView
from drf_spectacular.utils import extend_schema

from core.pagination import CustomPageNumberPagination
from .serializers import UserAdminSerializer


UserModel = get_user_model()


class UserViewSet(ListModelMixin,
                  RetrieveModelMixin,
                  GenericViewSet):
    
    queryset = UserModel.objects \
        .prefetch_related('simulations') \
        .order_by('-date_joined', '-id') \
        .all()
    
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPageNumberPagination

    @extend_schema(
        description="Return a specific user's details"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Returns list of users with their simulation activity"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


