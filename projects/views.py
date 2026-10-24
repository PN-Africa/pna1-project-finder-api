from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend


from .models import Project, Simulation
from .pagination import CustomPageNumberPagination
from .filters import AvailableProjectFilter, ProjectFilter, SimulationFilter
from .serializers import (
    ProjectCreateSerializer,
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectPublicDetailSerializer,
    ProjectPublicListSerializer,
    SimulationCreateSerializer,
    SimulationDetailSerializer,
    SimulationListSerializer
)


class ProjectViewSet(RetrieveModelMixin,
                     ListModelMixin,
                     CreateModelMixin,
                     GenericViewSet):
    
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend]
    filterset_class = ProjectFilter

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Project.objects.filter(is_published=True)
        
        return Project.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
    
        if self.action == 'create':
            return ProjectCreateSerializer

        if self.action == 'retrieve':
            if not self.request.user.is_staff:
                return ProjectPublicDetailSerializer
            
            return ProjectDetailSerializer

        if self.action == 'available':
            return ProjectPublicListSerializer

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'available':
            return [IsAuthenticated()]
        
        return [IsAdminUser()]

    @extend_schema(
        description=("Returns all projects (published and unpublished) "
                     "to an admin user")
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description=("Returns a specific project to an authenticated user")
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description=("Creates a project. This action is reserved for admin users"),
        responses={201: ProjectDetailSerializer},
    )
    def create(self, request, *args, **kwargs):
        create_serializer = self.get_serializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        project = create_serializer.save()

        return_serializer = ProjectDetailSerializer(project)
        headers = self.get_success_headers(return_serializer.data)
        return Response(
            return_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    @extend_schema(
        description=(
            "Returns all projects available for simulation "
            "to an authenticated user. This includes published "
            "projects which have not been simulated by the current "
            "user (i.e projects that have previously been simulated " 
            "or are currently being simulated by the user are excluded)."
        ),
        responses={200: ProjectPublicListSerializer(many=True)}
    )
    @action(
        methods=['GET'],
        detail=False,
        filterset_class=AvailableProjectFilter
    )
    def available(self, request):
        # build queryset
        simulations = Simulation.objects.filter(user=request.user)
        simulated_project_ids = [s.project_id for s in simulations]
        published_projects = self.get_queryset() \
            .filter(is_published=True) \
            .exclude(id__in=simulated_project_ids)

        queryset = self.filter_queryset(published_projects)

        # build and return response
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SimulationViewSet(ListModelMixin,
                        RetrieveModelMixin,
                        CreateModelMixin,
                        GenericViewSet):
    
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend]
    filterset_class = SimulationFilter

    def get_queryset(self):
        return Simulation.objects.filter(user=self.request.user) \
            .select_related('project') \
            .prefetch_related(
                'project__stakeholders',
                'project__tasks',
                'project__deliverables',
            )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SimulationCreateSerializer

        if self.action == 'list':
            return SimulationListSerializer

        if self.action == 'retrieve':
            return SimulationDetailSerializer
    
    @extend_schema(
        description=(
            "Creates/starts a simulation on the provided project's ID "
            "for the current user."
        ),
        responses={201: SimulationDetailSerializer},
    )
    def create(self, request, *args, **kwargs):
        create_serializer = self.get_serializer(
            data=request.data,
            context={'user': request.user}
        )
        create_serializer.is_valid(raise_exception=True)
        simulation = create_serializer.save()

        return_serializer = SimulationDetailSerializer(simulation)
        headers = self.get_success_headers(return_serializer.data)
        return Response(
            return_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @extend_schema(
        description=(
            "Returns all simulations (in progess and submitted) "
            "for the current user."
        )
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description=(
            "Returns a specific simulation for the current user"
        )
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    
        