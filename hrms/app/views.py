from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import *
from .models import Employee,LearningPlan,PerformanceReview, Department
from .forms import LearningForm, EmployeeCreateForm,EmployeeAdminUpdateForm,LearningReviewForm,LearningUpdateForm,EmployeeUpdateForm,PerformanceReviewAdminForm,PerformanceReviewForm,PerformanceReviewUpdateForm,PerformanceReviewAdminUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.mail import send_mail
from .filters import employee_filter


class CreateEmp(LoginRequiredMixin,SuccessMessageMixin,CreateView):
    model = Employee
    form_class = EmployeeCreateForm
    success_url = reverse_lazy('app:dashboard')
    template_name = 'app/create.html'
    login_url = reverse_lazy('app:login')
    # success_message = 'Employee Created Successfully'
    def get_success_message(self, cleaned_data):
        return f'{cleaned_data.get("first_name")} {cleaned_data.get("last_name")} added as an Employee'

    

def loginUser(request):
    if request.method == 'POST':
        user = authenticate(request, username = request.POST['username'], password = request.POST['password'], )
        if user:
            login(request,user)
            messages.success(request,'You are Logged In')
            return redirect('app:dashboard')
        else:
            raise PermissionDenied('Wrong Credentials')
    return render(request,'app/login.html')

@login_required(login_url='app:login')
def logoutUser(request):
    logout(request)
    messages.success(request,'You are Logged Out')
    return redirect('app:login')

class DashboardView(LoginRequiredMixin,ListView):
    model = Employee
    template_name = 'app/dashboard.html'
    login_url = reverse_lazy('app:login')

    def get_queryset(self):
        employee = self.request.user.employee
        if employee.role in ['CEO','HR']:
            self.filter = employee_filter(self.request.GET, queryset = super().get_queryset())
            return Employee.objects.all() and self.filter.qs
        else:
            return Employee.objects.filter(user = self.request.user)
        
        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ceo or hr filter
        context['is_ceo_or_hr'] = self.request.user.employee.role in ['CEO','HR']
        user = self.request.user.employee
        # pending count
        context['pending'] = PerformanceReview.objects.filter(graded = 'PENDING', employee = user).count()
        # managers count
        employees = context['object_list']
        manager_ids = {emp.reporting_to_id for emp in employees if emp.reporting_to_id}
        context['managers'] = len(manager_ids)
        # print(f'Debug: Manager Count = {len(manager_ids)}')
        # department count
        depts = {emp.department for emp in employees}
        context['depts'] = len(depts)
        # have meeting or not 
        meetings = LearningPlan.objects.filter(schedule_meeting__isnull=False, employee=user)
        if meetings.exists():
            context['meeting'] = meetings
        else:
            context['meeting'] = None
        # avg rating 
        context['performance'] = PerformanceReview.objects.filter(employee = self.request.user.employee)
        performance = context['performance']
        for item in performance:
            if (item.responsibility_rating and item.communication_rating and item.quality_rating and item.communication_rating):
                context['avg_rating'] = (item.responsibility_rating + item.communication_rating + item.quality_rating + item.communication_rating) / 4

        # Filter Context 
        if self.request.user.employee.role in ['CEO','HR']:
            context['filter'] = self.filter
            context['departments'] = Department.objects.all()
            context['role_choices'] = Employee.ROLE_CHOICES
        return context


class LearningPlanView(LoginRequiredMixin,ListView):
    model = LearningPlan
    context_object_name = 'data'
    login_url = reverse_lazy('app:login')
    template_name = 'app/learnview.html'

    def get_queryset(self):
        if self.request.user.employee.role in ['CEO','HR']:
            return LearningPlan.objects.all()
        else:
            return LearningPlan.objects.filter(employee = self.request.user.employee )
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = LearningPlan.objects.filter(employee = self.request.user.employee)
        context['is_ceo_or_hr'] = self.request.user.employee.role in ['CEO','HR']
        context['active_plans'] = data.filter(status = 'APPROVED').count()
        return context

# @login_required(login_url=reverse_lazy('app:login'))
# def empUpdateEmp(request,pk):
#     data = get_object_or_404(Employee,pk=pk)
#     if request.method == 'POST':
#         form = EmployeeUpdateForm(request.POST or None, instance=data)
#         if form.is_valid():
#             form.save()
#             return redirect('app:dashboard')
#         else:
#             form = EmployeeUpdateForm(instance=data)
#     return render(request,'app/empupdate.html',{'form':form})

# @login_required(login_url=reverse_lazy('app:login'))
# def adminUpdateEmp(request,pk):
#     data = get_object_or_404(Employee,pk=pk)
#     if request.method == 'POST':
#         form = EmployeeUpdateByAdminForm(request.POST or None, instance=data)
#         if form.is_valid():
#             form.save()
#             return redirect('app:dashboard')
#         else:
#             form = EmployeeUpdateByAdminForm(instance=data)
#     return render(request,'app/empupdate.html',{'form':form})

class EmpUpdateEmpView(LoginRequiredMixin,SuccessMessageMixin,UpdateView):
    model = Employee
    login_url = reverse_lazy('app:login')
    success_url = reverse_lazy('app:dashboard')
    template_name = 'app/empupdate.html'
    success_message = 'Employee Profile Updated'

    def get_form_class(self):
        employee = self.request.user.employee
        if employee.role in ['CEO','HR']:
            return EmployeeAdminUpdateForm
        else:
            return EmployeeUpdateForm
    
    def get_object(self):
        if self.request.user.employee.role in ['CEO','HR']:
            return get_object_or_404(Employee, pk = self.kwargs['pk'])
        else:
            return self.request.user.employee
        
    def get_queryset(self):
        if self.request.user.employee.role in ['CEO','HR']:
            return Employee.objects.all()
        else:
            return Employee.objects.filter(user = self.request.user)
    
    def form_valid(self, form):
        fresh_employee = get_object_or_404(Employee, pk=form.instance.pk)
    
        new_role = form.cleaned_data.get('role')
        
        if fresh_employee.role == 'CEO' and new_role != 'CEO':
            if fresh_employee.user == self.request.user:
                form.add_error('role', 'You cannot demote yourself from CEO')
                return self.form_invalid(form)
        
        if form.cleaned_data.get('role') == 'CEO' and form.cleaned_data.get('reporting_to'):
            form.add_error('reporting_to', 'CEO cannot report to anyone')
            return self.form_invalid(form)
        return super().form_valid(form)



class LearningCreateView(LoginRequiredMixin,SuccessMessageMixin,CreateView):
    model = LearningPlan
    form_class = LearningForm
    success_url = reverse_lazy('app:learnplan')
    login_url = reverse_lazy('app:login')
    template_name = 'app/createlp.html'
    success_message = 'Learning Plan Created'

    def form_valid(self, form):
        form.instance.employee = self.request.user.employee
        return super().form_valid(form)

class LearningUpdateByEmp(LoginRequiredMixin,SuccessMessageMixin,UpdateView,):
    model = LearningPlan
    form_class = LearningUpdateForm
    login_url = reverse_lazy('app:login')
    success_url = reverse_lazy('app:learnplan')
    template_name = 'app/updatelp.html'
    success_message = 'Learning Plan Updated'

    def get_queryset(self):
        return LearningPlan.objects.filter(employee__user = self.request.user)


class LearningReView(LoginRequiredMixin, SuccessMessageMixin,UpdateView,):
    model = LearningPlan
    form_class = LearningReviewForm
    login_url = reverse_lazy('app:login')
    success_url = reverse_lazy('app:subordinates')
    template_name = 'app/reviewlp.html'
    success_message = 'Learning Plan Approved'
    
    def get_object(self):
        learning_plan = get_object_or_404(LearningPlan, pk=self.kwargs['pk'])
        reviewer = self.request.user.employee
        
        if learning_plan.employee.reporting_to != reviewer:
            raise PermissionDenied("You can only review your subordinate's plans")
        return learning_plan
    
    def form_valid(self, form):
        if form.instance.status == 'APPROVED':
            form.instance.approved_by = self.request.user.employee
        return super().form_valid(form)
    
class SubordinateView(LoginRequiredMixin,ListView):
    model = LearningPlan
    template_name = 'app/subordinate.html'
    login_url = reverse_lazy('app:login')
    context_object_name = 'plans'

    def get_queryset(self):
        manager = self.request.user.employee
        has_manager = Employee.objects.filter(reporting_to = manager).exists()
        if not has_manager:
            return LearningPlan.objects.none()
        subordinate = Employee.objects.filter(reporting_to = manager)
        return LearningPlan.objects.filter(employee__in=subordinate).order_by('status')
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        plans =context['plans']
        context['pending_count'] = plans.filter(status = 'PENDING')
        context['approved_count'] = plans.filter(status='APPROVED')
        context['review_count'] = plans.filter(status='REVIEW')
        context['subordinate_count']=Employee.objects.filter(reporting_to=self.request.user.employee).count()
        return context
    
class AllLearningView(LoginRequiredMixin,ListView):
    model = LearningPlan
    template_name = 'app/all_learning_plans.html'
    login_url = reverse_lazy('app:login')
    context_object_name = 'plans'
    def get_queryset(self):
        employee = self.request.user.employee
        if employee.role in ['CEO','HR']:
            return LearningPlan.objects.all()
        else:
            return LearningPlan.objects.none()
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_ceo_or_hr'] = self.request.user.employee.role in ['CEO','HR']
        return context
    
def roles(request):
    ceo_hr = ['CEO','HR']
    return render(request,'app/nav.html',{'ceo_hr':ceo_hr})

class LearnPlanDetailView(LoginRequiredMixin, DetailView):
    model = LearningPlan
    template_name = 'app/specific.html'
    login_url = reverse_lazy('app:login')
    context_object_name = 'plans'


class CreatePerformance(LoginRequiredMixin,SuccessMessageMixin,CreateView):
    model = PerformanceReview
    template_name = 'app/createpr.html'
    login_url = reverse_lazy('app:login')
    success_url = reverse_lazy('app:dashboard')
    success_message = 'Performance Review Submitted'
    
    def get_form_class(self):
        if not self.request.user.employee.role in['CEO']:
            return PerformanceReviewForm
        
    def form_valid(self, form):
        form.instance.employee = self.request.user.employee
        return super().form_valid(form)
        
# all subordinates review 
class PerformanceList(LoginRequiredMixin,ListView):
    model = PerformanceReview
    login_url = reverse_lazy('app:login')
    context_object_name = 'performances'
    template_name = 'app/perflist.html'

    def get_queryset(self):
        manager = self.request.user.employee
        subordinate = Employee.objects.filter(reporting_to = manager)
        if not subordinate.exists():
            return PerformanceReview.objects.none()
        return PerformanceReview.objects.filter(employee__in=subordinate)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manager = self.request.user.employee
        subordinate = Employee.objects.filter(reporting_to = manager)
        data =  PerformanceReview.objects.filter(employee__in=subordinate)
        context['subordinate_count'] = subordinate.count()
        context['pending_grading'] = data.filter(graded = 'PENDING').count()
        return context
    
# Email 

# def performance_grade_email(performance):
#     if performance.graded == 'GRADED':
#         subject = 'Your Performance Review is Ready'
#         status = 'graded'
#         action = 'view'

#         message = f'''
#         Hello, {performance.employee.user.get_full_name()},
        
#         Your performance review has been {status}.
        
#         Overall Score: { performance.average_score} / 5
        
#         Login to {action} your grades.
        
#         Best Regards,
#         {performance.commented_by.user.get_full_name() if performance.commented_by else 'HR'}'''

#         send_mail(
#             subject = subject,
#             message=message,
#             from_email='hr@enkefalos.com',
#             recipient_list=[performance.employee.user.email]
#         )

class GradePerformance(LoginRequiredMixin,SuccessMessageMixin,UpdateView):
    model = PerformanceReview
    form_class = PerformanceReviewAdminForm
    login_url = reverse_lazy('app:login')
    success_url = reverse_lazy('app:perflist')
    template_name = 'app/gradeperf.html'
    success_message = 'Performance Graded'

    def get_object(self):
        grade_performance = get_object_or_404(PerformanceReview, pk = self.kwargs['pk'])
        grader = self.request.user.employee

        if grade_performance.employee.reporting_to != grader:
            raise PermissionDenied('You can only grade your subordinates')
        return grade_performance
    
    def form_valid(self, form):
        form.instance.commented_by = self.request.user.employee
        # self.object = form.save()
        # performance_grade_email(self.object)
        
        return super().form_valid(form)
    
class EmpUpdatePerformance(LoginRequiredMixin,SuccessMessageMixin, UpdateView,):
    model = PerformanceReview
    form_class = PerformanceReviewForm
    login_url = reverse_lazy('app:login')
    success_url = reverse_lazy('app:dashboard')
    template_name = 'app/updateperf.html'
    success_message = 'Performance Review Updated'
    
    def get_object(self):
        performance = get_object_or_404(PerformanceReview, pk=self.kwargs['pk'])
        if performance.employee.user != self.request.user:
            raise PermissionDenied('You can only edit your own performance review')
        if (performance.responsibility_rating or performance.communication_rating or 
            performance.quality_rating or performance.accountability_rating):
            raise PermissionDenied('Cannot edit after supervisor has graded')
        return performance


class DetailedPerformance(LoginRequiredMixin, DetailView):
    model = PerformanceReview
    login_url = reverse_lazy('app:login')
    template_name = 'app/detailperf.html'
    context_object_name = 'performance'

    def get_object(self):
        performance = get_object_or_404(PerformanceReview, pk=self.kwargs['pk'])
        currentuser = self.request.user.employee
        if (performance.employee.user != self.request.user and 
            performance.employee.reporting_to != currentuser and
            currentuser.role not in ['CEO', 'HR']):
            raise PermissionDenied('You do not have access to view this')
        return performance
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        performance = context['performance']
        current_user = self.request.user.employee
        context['can_edit'] = (performance.employee.user == self.request.user and 
                              not performance.responsibility_rating)
        context['can_grade'] = (performance.employee.reporting_to == current_user or
                               current_user.role in ['CEO', 'HR'])
        
        if (performance.responsibility_rating and performance.communication_rating and 
            performance.quality_rating and performance.accountability_rating):
            total = (performance.responsibility_rating + performance.communication_rating + 
                    performance.quality_rating + performance.accountability_rating)
            context['overall_score'] = total / 4
        else:
            context['overall_score'] = None
        
        return context

    
class UpdateGradePerformance(LoginRequiredMixin,SuccessMessageMixin, UpdateView):
    model = PerformanceReview
    form_class = PerformanceReviewAdminUpdateForm
    login_url = reverse_lazy('app:login')
    success_url = reverse_lazy('app:perflist')
    template_name = 'app/updategrade.html'
    success_message = 'Performance Grade Updated'
    
    def get_object(self):
        performance = get_object_or_404(PerformanceReview, pk=self.kwargs['pk'])
        grader = self.request.user.employee
        if (performance.employee.reporting_to != grader and
            grader.role not in ['CEO', 'HR']):
            raise PermissionDenied('You can only update grades for your subordinates')
        
        if not (performance.responsibility_rating and performance.communication_rating and
                performance.quality_rating and performance.accountability_rating):
            raise PermissionDenied('This review has not been graded yet')
        return performance
    
    def form_valid(self, form):
        if form.instance.comments:
            form.instance.commented_by = self.request.user.employee
        return super().form_valid(form)