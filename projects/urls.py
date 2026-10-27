from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ProjectAdminViewSet, ProjectViewSet, SimulationAdminViewSet, SimulationViewSet


router = SimpleRouter()
router.register('projects', ProjectViewSet, basename='project')
router.register('simulations', SimulationViewSet, basename='simulation')

admin_router = SimpleRouter()
admin_router.register('projects', ProjectAdminViewSet, basename='admin-project')
admin_router.register('simulations', SimulationAdminViewSet, basename='admin-simulation')

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', include(admin_router.urls))
]