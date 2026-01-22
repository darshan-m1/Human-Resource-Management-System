import django_filters
from .models import Department, Employee
from django.db.models import Q

class employee_filter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='Search')
    
    department = django_filters.ModelChoiceFilter(
        queryset=Department.objects.all(),
        empty_label = 'All Departments'
    )

    role = django_filters.ChoiceFilter(
        choices = Employee.ROLE_CHOICES,
        empty_label = 'All Roles'
    )

    class Meta:
        model = Employee
        fields = ['department','role']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(user__first_name__icontains = value) |
            Q(user__last_name__icontains = value) |
            Q(user__email__icontains = value))