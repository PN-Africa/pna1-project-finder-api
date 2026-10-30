from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from .views import DeliverableSubmissionAdminViewSet, DeliverableSubmissionViewSet, ProjectAdminViewSet, ProjectViewSet, SimulationAdminViewSet, SimulationViewSet, StatsView


router = SimpleRouter()
router.register('projects', ProjectViewSet, basename='project')
router.register('simulations', SimulationViewSet, basename='simulation')

simulations_router = NestedSimpleRouter(router, 'simulations', lookup='simulation')
simulations_router.register('uploads', DeliverableSubmissionViewSet, 'simulation-uploads')

admin_router = SimpleRouter()
admin_router.register('projects', ProjectAdminViewSet, basename='admin-project')
admin_router.register('simulations', SimulationAdminViewSet, basename='admin-simulation')

admin_simulations_router = NestedSimpleRouter(admin_router, 'simulations', lookup='simulation')
admin_simulations_router.register('uploads', DeliverableSubmissionAdminViewSet, 'admin-simulation-uploads')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(simulations_router.urls)),
    path('admin/', include(admin_router.urls)),
    path('admin/', include(admin_simulations_router.urls)),
    path('admin/stats/', StatsView.as_view(), name='stats'),
]