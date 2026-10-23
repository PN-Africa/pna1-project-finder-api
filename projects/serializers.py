from django.db import transaction

from rest_framework import serializers

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
class ProjectPublicListSerializer(serializers.ModelSerializer):
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
class ProjectPublicDetailSerializer(serializers.ModelSerializer):
    stakeholders = StakeholderSerializer(many=True)
    tasks = TaskSerializer(many=True)
    deliverables = DeliverableSerializer(many=True)

    class Meta:
        model = Project
        fields = ['id', *public_project_fields]


# admin - list
class ProjectListSerializer(ProjectPublicListSerializer):
    # is_published = serializers.BooleanField()

    class Meta(ProjectPublicListSerializer.Meta):
        fields = [
            *ProjectPublicListSerializer.Meta.fields,
            'is_published'
        ]


# admin - create
class ProjectCreateSerializer(serializers.ModelSerializer):
    stakeholders = serializers.ListField(
        child=serializers.CharField(min_length=2, allow_blank=False,),
        allow_empty=False,
        required=True,
    )
    tasks = serializers.ListField(
        child=serializers.CharField(max_length=300, allow_blank=False),
        allow_empty=False,
        required=True,
    )
    deliverables = DeliverableSerializer(
        many=True,
        allow_empty=False,
        required=True,
    )

    class Meta:
        model = Project
        fields = [*public_project_fields, 'is_published']

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
                    name=d.get('name'),
                    description=d.get('description', None),
                    project=project,
                )
                for d in deliverables
            ]

            Stakeholder.objects.bulk_create(stakeholder_objs)
            Task.objects.bulk_create(task_objs)
            Deliverable.objects.bulk_create(deliverable_objs)

        return project


class ProjectDetailSerializer(ProjectPublicDetailSerializer):
    class Meta(ProjectPublicDetailSerializer.Meta):
        fields = [
            *ProjectPublicDetailSerializer.Meta.fields,
            'is_published',
        ]


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
    project = ProjectPublicListSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)

    class Meta:
        model = Simulation
        fields = [
            'id',
            'project',
            'user_id',
            'status',
            'started_at',
            'submitted_at',
        ]


class SimulationDetailSerializer(SimulationListSerializer):
    project = ProjectPublicDetailSerializer(read_only=True)

    
            