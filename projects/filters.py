import django_filters

from projects.models import Simulation


class ProjectFilter(django_filters.FilterSet):
    industry = django_filters.CharFilter(
        field_name='industry',
        lookup_expr='iexact'
    )
    difficulty = django_filters.CharFilter(
        field_name='difficulty_level',
        lookup_expr='iexact'
    )


class ProjectAdminFilter(django_filters.FilterSet):
    industry = django_filters.CharFilter(
        field_name='industry',
        lookup_expr='iexact'
    )
    difficulty = django_filters.CharFilter(
        field_name='difficulty_level',
        lookup_expr='iexact'
    )
    is_published = django_filters.BooleanFilter(
        field_name='is_published',
        lookup_expr='exact'
    )


class SimulationFilter(django_filters.FilterSet):
    industry = django_filters.CharFilter(
        field_name='project__industry',
        lookup_expr='iexact',
    )
    difficulty = django_filters.CharFilter(
        field_name='project__difficulty_level',
        lookup_expr='iexact'
    )


class SimulationAdminFilter(django_filters.FilterSet):
    user_id = django_filters.UUIDFilter(
        field_name='user__id',
        lookup_expr='exact',
    )