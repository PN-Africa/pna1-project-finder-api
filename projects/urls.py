from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ProjectViewSet, SimulationViewSet


router = SimpleRouter()
router.register('projects', ProjectViewSet, basename='project')
router.register('simulations', SimulationViewSet, basename='simulation')

urlpatterns = [
    path("", include(router.urls)),
]