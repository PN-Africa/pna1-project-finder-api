from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
)
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend


from core.pagination import CustomPageNumberPagination
from .models import DeliverableSubmission, Project, Simulation, get_choices
from .filters import (
    ProjectFilter,
    ProjectAdminFilter,
    SimulationAdminFilter,
    SimulationFilter
)
from .serializers import (
    DeliverableSubmissionSerializer,
    ProjectCreateSerializer,
    ProjectAdminListSerializer,
    ProjectAdminDetailSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectStatusSerializer,
    SimulationAdminSerializer,
    SimulationCreateSerializer,
    SimulationDetailSerializer,
    SimulationListSerializer,
    SimulationSubmitSerializer,
    SimulationSubmitResponseSerializer,
    ChoicesResponseSerializer,
    StatsSerializer,
)

# handles regular user actions for projects
class ProjectViewSet(RetrieveModelMixin,
                     ListModelMixin,
                     GenericViewSet):
    
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend]
    filterset_class = ProjectFilter

    def get_queryset(self):
        simulations = Simulation.objects.filter(user=self.request.user)
        simulated_project_ids = [s.project_id for s in simulations]

        return Project.objects \
            .filter(is_published=True) \
            .exclude(id__in=simulated_project_ids) \
            .order_by('-created_at', '-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer

        if self.action == 'retrieve':
            return ProjectDetailSerializer

        # return ProjectPublicListSerializer

    @extend_schema(
        description=("Returns a specific project to an authenticated user")
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        description=(
            "Returns all projects available for simulation "
            "to an authenticated user. This includes published "
            "projects which have not been simulated by the current "
            "user (i.e projects that have previously been simulated " 
            "or are currently being simulated by the user are excluded)."
        ),
        responses={200: ProjectListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

        # # build queryset
        # simulations = Simulation.objects.filter(user=request.user)
        # simulated_project_ids = [s.project_id for s in simulations]
        # published_projects = self.get_queryset() \
        #     .filter(is_published=True) \
        #     .exclude(id__in=simulated_project_ids)

        # queryset = self.filter_queryset(published_projects)

        # # build and return response
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        # serializer = self.get_serializer(queryset, many=True)
        # return Response(serializer.data)

    @extend_schema(
        description=(
            "Returns information about the project industry and difficulty "
            "level string choices accepted by the API."
        ),
        responses={200: ChoicesResponseSerializer}
    )
    @action(methods=['GET'], detail=False)
    def choices(self, request):
        return Response(
            {
                'project_industries': get_choices(Project.Industry.choices),
                'project_difficulty_levels': get_choices(
                    Project.DifficultyLevel.choices,
                )
            }
        )


# handles admin actions for projects
class ProjectAdminViewSet(ModelViewSet):
    
    queryset = Project.objects \
        .prefetch_related('simulations') \
        .order_by('-created_at', '-id') \
        .all()
    
    permission_classes = [IsAdminUser]
    pagination_class = CustomPageNumberPagination
    
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProjectAdminFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectAdminListSerializer
    
        if self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateSerializer

        if self.action == 'retrieve':
            return ProjectAdminDetailSerializer

        if self.action == 'update_status':
            return ProjectStatusSerializer

        # return ProjectPublicListSerializer
    
    @extend_schema(
        description=(
            "Returns all projects (published and unpublished) "
            "to an admin user"
        )
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description=("Returns a specific project to an admin user")
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description=("Creates a project. This action is reserved for admin users"),
        responses={201: ProjectAdminDetailSerializer},
    )
    def create(self, request, *args, **kwargs):
        create_serializer = self.get_serializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        project = create_serializer.save()

        return_serializer = ProjectAdminDetailSerializer(project)
        headers = self.get_success_headers(return_serializer.data)
        return Response(
            return_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @extend_schema(
        description=(
            "Edits an existing project. "
            "This action is reserved for admin users"
        ),
        responses={201: ProjectAdminDetailSerializer},
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        update_serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        update_serializer.is_valid(raise_exception=True)
        project = update_serializer.save()

        return_serializer = ProjectAdminDetailSerializer(project)
        return Response(return_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        description='Publish or unpublish a specific project',
        responses={200: ProjectAdminListSerializer}
    )
    @action(detail=True, methods=["POST"], url_path='status')
    def update_status(self, request, pk=None):
        instance = self.get_object()
        
        status_update_serializer = self.get_serializer(
            instance,
            data=request.data,
        )
        status_update_serializer.is_valid(raise_exception=True)
        project = status_update_serializer.save()
        
        return_serializer = ProjectAdminListSerializer(project)
        return Response(return_serializer.data, status=status.HTTP_200_OK)


# handles regular user actions for simulations
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
            ) \
            .order_by('-started_at', '-id')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SimulationCreateSerializer

        if self.action == 'list':
            return SimulationListSerializer

        if self.action == 'retrieve':
            return SimulationDetailSerializer

        if self.action == 'submit':
            return SimulationSubmitSerializer
    
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

    @extend_schema(
        description="Submit the simulation referenced in the url path",
        responses={200: SimulationSubmitResponseSerializer}
    )
    @action(methods=['POST'], detail=True)
    def submit(self, request, pk=None):
        instance = self.get_object()
        submit_serializer = self.get_serializer(
            instance,
            data=request.data,
        )

        submit_serializer.is_valid(raise_exception=True)
        simulation = submit_serializer.save()

        return_serializer = SimulationSubmitResponseSerializer(simulation)
        headers = self.get_success_headers(return_serializer.data)
        return Response(
            return_serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )
    
    
# handles admin action for simulations
class SimulationAdminViewSet(ListModelMixin,
                             RetrieveModelMixin,
                             GenericViewSet):
    
    queryset = Simulation.objects \
        .select_related('user', 'project') \
        .order_by('-started_at', '-id') \
        .all()
    
    serializer_class = SimulationAdminSerializer
    permission_classes = [IsAdminUser]

    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = SimulationAdminFilter

    @extend_schema(
        description=(
            "Returns all simulations to an admin user"
        )
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description=(
            "Returns a specific simulation to an admin user"
        )
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class DeliverableSubmissionViewSet(ModelViewSet):
    serializer_class = DeliverableSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        simulation = self.get_simulation()

        return DeliverableSubmission.objects \
            .filter(
                simulation_id=simulation.id,
                simulation__user=self.request.user
            ) \
            .order_by('-uploaded_at', '-id')

    def get_simulation(self):
        try:
            return Simulation.objects.get(
                pk=self.kwargs['simulation_pk'],
                user=self.request.user
            )
        except Simulation.DoesNotExist:
            raise NotFound('Simulation does not exist.')

    def check_simulation_status(self):
        simulation = self.get_simulation()

        if simulation.status == Simulation.Status.SUBMITTED:
            raise PermissionDenied(
                "This simulation has already been submitted. "
                "It's deliverables can no longer be modified."
            )

        return simulation

    def perform_create(self, serializer):
        simulation = self.check_simulation_status()
        serializer.save(simulation=simulation)

    def perform_update(self, serializer):
        self.check_simulation_status()
        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        self.check_simulation_status()
        return super().perform_destroy(instance)

    @extend_schema(
        description='Returns a list of file uploads for the referenced simulation'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description='Returns a specific file upload'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description='Uploads a new file for the referenced simulation'
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description='Replaces the file uploads for a given upload'
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description='Deletes/removes a file upload'
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class DeliverableSubmissionAdminViewSet(ListModelMixin,
                                        RetrieveModelMixin,
                                        GenericViewSet):
    
    serializer_class = DeliverableSubmissionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return DeliverableSubmission.objects \
            .filter(simulation_id=self.kwargs['simulation_pk'],) \
            .order_by('uploaded_at')  

    @extend_schema(
        description='Returns a list of file uploads for the referenced simulation'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description='Returns a specific file upload'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class StatsView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        description=(
            'Returns dashboard statistics for projects and simulations.'
        ),
        responses={200: StatsSerializer}
    )
    def get(self, request):
        serializer = StatsSerializer({})
        return Response(serializer.data, status=status.HTTP_200_OK)