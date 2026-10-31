from django.db import models
from django.conf import settings

from core.models import BaseModel


def get_choices(choices):
    return [
        {'value': value, 'label': label}
        for value, label in choices
    ]


class Project(BaseModel):
    class DifficultyLevel(models.TextChoices):
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'

    class Industry(models.TextChoices):
        TECH = 'technology', 'Technology'
        HEALTHCARE = 'healthcare', 'Healthcare'
        FINTECH = 'fintech', 'Fintech'
        ECOMMERCE = 'ecommerce', 'E-commerce'
        REAL_ESTATE = 'real_estate', 'Real Estate'
        EDTECH = 'edtech', 'EdTech'

    title = models.CharField(max_length=255)
    scenario_name = models.CharField(max_length=255, null=True)
    scenario_description = models.TextField()
    business_problem = models.TextField()
    objective = models.TextField()
    professional_role = models.CharField(max_length=255)
    is_published = models.BooleanField(default=False)
    duration_in_days = models.PositiveIntegerField(null=True)

    industry = models.CharField(max_length=255, choices=Industry.choices)
    difficulty_level = models.CharField(max_length=255, choices=DifficultyLevel.choices)
    brief = models.FileField(upload_to='briefs/', null=True)


class Stakeholder(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='stakeholders')
    name = models.CharField(max_length=255)


class Task(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    description = models.TextField()


class Deliverable(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='deliverables')
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)


class Simulation(BaseModel):
    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', 'In Progress'
        SUBMITTED = 'submitted', 'Submitted'

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        related_name='simulations'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='simulations'
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.IN_PROGRESS
    )
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True)


class DeliverableSubmission(BaseModel):
    MAX_SIZE_BYTES = 10 * 1024 * 1024

    simulation = models.ForeignKey(
        Simulation,
        on_delete=models.CASCADE,
        related_name='deliverable_submissions'
    )
    file = models.FileField(upload_to='deliverables/')
    uploaded_at = models.DateTimeField(auto_now=True)