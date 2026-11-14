from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from core.pagination import CustomPageNumberPagination
from .serializers import UserAdminSerializer, VerifyPasswordSerializer
from .services import clear_auth_cookies, deactivate_user, delete_user, send_account_deactivation_email, send_account_deletion_email


UserModel = get_user_model()


class UserAdminViewSet(ListModelMixin,
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


class AccountDeactivationView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VerifyPasswordSerializer

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(
            data=request.data,
            context={'user': user}
        )
        serializer.is_valid(raise_exception=True)

        deactivate_user(user)

        send_account_deactivation_email(request, user)

        response = Response(
            {'detail': 'Account deactivated successfully.'},
            status=status.HTTP_200_OK,
        )

        return clear_auth_cookies(response)


class AccountDeletionView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VerifyPasswordSerializer

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(
            data=request.data,
            context={'user': user}
        )
        serializer.is_valid(raise_exception=True)

        email = user.email
        name = user.first_name

        delete_user(user)

        send_account_deletion_email(request, email, name)

        response = Response(status=status.HTTP_204_NO_CONTENT)
        
        return clear_auth_cookies(response)

