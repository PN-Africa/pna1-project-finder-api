from django.db import transaction
from django.utils import timezone

from rest_framework import serializers

from accounts.serializers import UserAdminSerializer

from .models import Deliverable, Project, Simulation, Stakeholder, Task


public_project_fields = [
        'title',
        'scenario_name',
        'scenario_description',
        'business_problem',
        'objective',
        'professional_role',
        'duration_in_days',
        'industry',
        'difficulty_level',
        'stakeholders',
        'tasks',
        'deliverables',
    ]


class StakeholderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stakeholder
        fields = ['id', 'name']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'description']


class DeliverableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deliverable
        fields = ['id', 'name', 'description']


# user list
class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'duration_in_days',
            'industry',
            'difficulty_level',
        ]
        

# user detail
class ProjectDetailSerializer(serializers.ModelSerializer):
    # stakeholders = StakeholderSerializer(many=True)
    # tasks = TaskSerializer(many=True)
    # deliverables = DeliverableSerializer(many=True)

    stakeholders = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()
    deliverables = serializers.SerializerMethodField()

    def get_stakeholders(self, instance) -> list[str]:
        return [s.name for s in instance.stakeholders.all()]
        return 10

    def get_tasks(self, instance) -> list[str]:
        return [t.description for t in instance.tasks.all()]
        return 20

    def get_deliverables(self, instance) -> list[str]:
        return [d.name for d in instance.deliverables.all()]
        return 30


    class Meta:
        model = Project
        fields = ['id', *public_project_fields]


# admin - list
class ProjectAdminListSerializer(ProjectListSerializer):
    simulations_count = serializers.SerializerMethodField()

    def get_simulations_count(self, instance) -> int:
        return instance.simulations.count()

    class Meta(ProjectListSerializer.Meta):
        fields = [
            *ProjectListSerializer.Meta.fields,
            'is_published',
            'simulations_count',
        ]


# admin - detail
class ProjectAdminDetailSerializer(ProjectDetailSerializer):
    class Meta(ProjectDetailSerializer.Meta):
        fields = [
            *ProjectDetailSerializer.Meta.fields,
            'is_published',
        ]


# admin - create/update
class ProjectCreateSerializer(serializers.ModelSerializer):
    stakeholders = serializers.ListField(
        child=serializers.CharField(max_length=300, allow_blank=False,),
        allow_empty=False,
        required=True,
        write_only=True,
    )
    tasks = serializers.ListField(
        child=serializers.CharField(max_length=300, allow_blank=False),
        allow_empty=False,
        required=True,
        write_only=True,
    )
    deliverables = serializers.ListField(
        child=serializers.CharField(max_length=300, allow_blank=False),
        allow_empty=False,
        required=True,
        write_only=True,
    )

    class Meta:
        model = Project
        fields = [*public_project_fields]

    def _construct_child_objects(self, project, stakeholders, tasks, deliverables):
        stakeholder_objs = [
            Stakeholder(name=s, project=project) 
            for s in stakeholders
        ]
        task_objs = [
            Task(description=t, project=project)
            for t in tasks
        ]
        deliverable_objs = [
            Deliverable(
                name=d,
                # description=d.get('description', None),
                project=project,
            )
            for d in deliverables
        ]

        return stakeholder_objs, task_objs, deliverable_objs

    def create(self, validated_data):
        stakeholders = validated_data.pop('stakeholders', [])
        tasks = validated_data.pop('tasks', [])
        deliverables = validated_data.pop('deliverables', [])
        
        with transaction.atomic():
            project = Project.objects.create(**validated_data)

            stakeholder_objs = [
                Stakeholder(name=s, project=project) 
                for s in stakeholders
            ]
            task_objs = [
                Task(description=t, project=project)
                for t in tasks
            ]
            deliverable_objs = [
                Deliverable(
                    name=d,
                    project=project,
                    # description=d.get('description', None),
                )
                for d in deliverables
            ]

            Stakeholder.objects.bulk_create(stakeholder_objs)
            Task.objects.bulk_create(task_objs)
            Deliverable.objects.bulk_create(deliverable_objs)

        return project

    def update(self, instance, validated_data):
        stakeholders = validated_data.pop('stakeholders', None)
        tasks = validated_data.pop('tasks', None)
        deliverables = validated_data.pop('deliverables', None)
        
        with transaction.atomic():
            for field, value in validated_data.items():
                setattr(instance, field, value)

            instance.save()

            if stakeholders is not None:
                instance.stakeholders.all().delete()
                Stakeholder.objects.bulk_create([
                    Stakeholder(name=s, project=instance) 
                    for s in stakeholders
                ])

            if tasks is not None:
                instance.tasks.all().delete()
                Task.objects.bulk_create([
                    Task(description=t, project=instance)
                    for t in tasks
                ])

            if deliverables is not None:
                instance.deliverables.all().delete()
                Deliverable.objects.bulk_create([
                    Deliverable(
                        name=d,
                        project=instance,
                        # description=d.get('description', None),
                    )
                    for d in deliverables
                ])

        return instance


class SimulationCreateSerializer(serializers.Serializer):
    project_id = serializers.UUIDField(required=True)

    def validate_project_id(self, project_id):
        user = self.context['user']
        has_existing_simulation = Simulation.objects.filter(
            user=user,
            project_id=project_id
        ).exists()

        if has_existing_simulation:
            raise serializers.ValidationError(
                "The current user already has a simulation for the "
                "referenced project"
            )

        is_unpublished_project = Project.objects.filter(
            id=project_id,
            is_published=False,
        ).exists()

        if is_unpublished_project:
            raise serializers.ValidationError(
                "Invalid project id."
            )

        return project_id

    def create(self, validated_data):
        return Simulation.objects.create(
            project_id=validated_data['project_id'],
            user=self.context['user'],
        )


class SimulationListSerializer(serializers.ModelSerializer):
    project = ProjectListSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)
    submitted_deliverables_count = serializers.SerializerMethodField()

    def get_submitted_deliverables_count(self, instance) -> int:
        return instance.deliverable_submissions.count()

    class Meta:
        model = Simulation
        fields = [
            'id',
            'project',
            'user_id',
            'status',
            'started_at',
            'submitted_at',
            'submitted_deliverables_count',
        ]


class SimulationDetailSerializer(SimulationListSerializer):
    project = ProjectDetailSerializer(read_only=True)

    
class SimulationSubmitSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        if instance.submitted_at is not None:
            raise serializers.ValidationError(
                {'detail': 'Simulation has already been submitted.'}
            )

        # validate deliverables have been submitted -- yet to be done

        instance.submitted_at = timezone.now()
        instance.status = Simulation.Status.SUBMITTED
        instance.save()

        return instance


class SimulationSubmitResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Simulation
        fields = [
            'id',
            'project_id',
            'user_id',
            'status',
            'started_at',
            'submitted_at'
        ]


class ChoiceSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()

class ChoicesResponseSerializer(serializers.Serializer):
    project_industries = serializers.ListField(
        child=ChoiceSerializer()
    )
    project_difficulty_levels = serializers.ListField(
        child=ChoiceSerializer()
    )


class SimulationAdminSerializer(SimulationListSerializer):
    user = UserAdminSerializer(read_only=True)

    class Meta(SimulationListSerializer.Meta):
        parent_fields = [*SimulationListSerializer.Meta.fields]
        f = [field for field in parent_fields if field != 'user_id']

        fields = [*f, 'user']