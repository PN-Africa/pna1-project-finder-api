from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import AccountDeactivationView, UserAdminViewSet, AccountDeletionView


router = SimpleRouter()
router.register('users', UserAdminViewSet, basename='user')

urlpatterns = [
    path('auth/user/deactivate/', AccountDeactivationView.as_view()),
    path('auth/user/delete', AccountDeletionView.as_view()),
    path('admin/', include(router.urls)),
]