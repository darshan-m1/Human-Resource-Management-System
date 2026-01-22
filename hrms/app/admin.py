from django.contrib import admin

from .models import Department,Employee,LearningPlan, PerformanceReview

# Register your models here.

admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(LearningPlan)
admin.site.register(PerformanceReview)