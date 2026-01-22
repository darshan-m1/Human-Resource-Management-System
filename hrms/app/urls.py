from django.urls import path
from .views import *

app_name = 'app'
urlpatterns = [
    path('create/',CreateEmp.as_view(),name='create'),
    path('dashboard/',DashboardView.as_view(),name='dashboard'),
    path('',loginUser,name='login'),
    path('employee/update',EmpUpdateEmpView.as_view(),name='empupdate1'),
    path('employee/<int:pk>/update',EmpUpdateEmpView.as_view(),name='empupdate2'),
    path('learningplan/',LearningPlanView.as_view(),name='learnplan'),
    path('create/learnings/',LearningCreateView.as_view(),name='createlp'),
    path('learnings/<int:pk>/update',LearningUpdateByEmp.as_view(),name='updatelp'),
    path('learnings/<int:pk>/review',LearningReView.as_view(),name='reviewlp'),
    path('subordinates/',SubordinateView.as_view(),name='subordinates'),
    path('learnings/',AllLearningView.as_view(),name='allPlans'),
    path('learnings/<int:pk>/employee/',LearnPlanDetailView.as_view(),name='learnplandeep'),
    path('logout/',logoutUser,name='logout'),
    path('performance/create/', CreatePerformance.as_view(), name='createpr'),
    path('performance/list/', PerformanceList.as_view(), name='perflist'),
    path('performance/<int:pk>/grade/', GradePerformance.as_view(), name='gradeperf'),
    path('performance/<int:pk>/edit/', EmpUpdatePerformance.as_view(), name='editperf'),
    path('performance/<int:pk>/', DetailedPerformance.as_view(), name='detailperf'),
    path('performance/<int:pk>/update-grade/', UpdateGradePerformance.as_view(), name='updategrade'),
]