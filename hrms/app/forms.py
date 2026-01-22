from django import forms
from .models import Employee,LearningPlan,PerformanceReview
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class EmployeeCreateForm(forms.ModelForm):
    username = forms.CharField(max_length=30,required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=20,required=True)
    last_name = forms.CharField(max_length=20,required=True)

    class Meta:
        model = Employee
        fields = ['department','role','reporting_to',]
        widgets = {
            'department': forms.Select(),
            'role':forms.Select(),
            'reporting_to':forms.Select(),
        }

    def clean_role(self):
        role = self.cleaned_data.get('role')
        
        if role == 'CEO':
            if Employee.objects.filter(role='CEO').exists():
                raise forms.ValidationError('There can only be one CEO in the system.')
        
        return role
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match')
        
        return cleaned_data
    
    def save(self,commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name = self.cleaned_data['last_name']
        )
        user.save()
        employee = super().save(commit=False)
        employee.user = user
        if commit:
            employee.save()
        return employee


class EmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['department'] 
        widgets = {
            'department': forms.Select(),
        }

class EmployeeAdminUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['department', 'role', 'reporting_to']
        widgets = {
            'department': forms.Select(),
            'role': forms.Select(),
            'reporting_to': forms.Select(),
        }

    def clean_role(self):
        role = self.cleaned_data.get('role')

        if role == 'CEO' and self.instance.role != 'CEO' and Employee.objects.filter(role = 'CEO').exists():
                raise forms.ValidationError('There can only be one CEO in the system.')
        
        old_role = self.instance.role
        if old_role == 'CEO' and role != 'CEO':
            raise ValidationError('Cannot Demote CEO')
        return role
    def clean_reporting_to(self):
        reporting_to = self.cleaned_data.get('reporting_to')
        role = self.cleaned_data.get('role')
        if role == 'CEO' and reporting_to:
            raise ValidationError('CEO cannot report to anyone')
        return reporting_to

class LearningForm(forms.ModelForm):
    class Meta:
        model = LearningPlan
        fields = ['completed_learning','planned_learning','quarter_date']
        widgets = {
            'completed_learning':forms.Textarea(attrs={'rows':4}),
            'planned_learning':forms.Textarea(attrs={'rows':4}),
            'quarter_date':forms.DateInput(attrs={'type':'date'}),
        }

class LearningUpdateForm(forms.ModelForm):
    class Meta:
        model = LearningPlan
        fields = ['completed_learning','planned_learning','quarter_date']
        widgets = {
            'completed_learning':forms.Textarea(attrs={'rows':4}),
            'planned_learning':forms.Textarea(attrs={'rows':4}),
            'quarter_date':forms.DateInput(attrs={'type':'date'}),
        }

class LearningReviewForm(forms.ModelForm):
    class Meta:
        model = LearningPlan
        fields = ['status','review_note','schedule_meeting']
        widgets = {
            'status':forms.Select(),
            'review_note':forms.Textarea(attrs={'rows':4}),
            'schedule_meeting':forms.DateInput(attrs={'type':'date'}),
        }

class PerformanceReviewForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = ['responsibilities','responsibility_self_review','communication','communication_self_review','quality','quality_self_review','accountability','accountability_self_review']
        widgets = {
            'responsibilities':forms.Textarea(attrs={'rows':3}),
            'responsibility_self_review':forms.Textarea(attrs={'rows':3}),
            'communication':forms.Textarea(attrs={'rows':3}),
            'communication_self_review':forms.Textarea(attrs={'rows':3}),
            'quality':forms.Textarea(attrs={'rows':3}),
            'quality_self_review':forms.Textarea(attrs={'rows':3}),
            'accountability':forms.Textarea(attrs={'rows':3}),
            'accountability_self_review':forms.Textarea(attrs={'rows':3}),
        }

class PerformanceReviewUpdateForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = ['responsibilities','responsibility_self_review','communication','communication_self_review','quality','quality_self_review','accountability','accountability_self_review']
        widgets = {
            'responsibilities':forms.Textarea(attrs={'rows':3}),
            'responsibility_self_review':forms.Textarea(attrs={'rows':3}),
            'communication':forms.Textarea(attrs={'rows':3}),
            'communication_self_review':forms.Textarea(attrs={'rows':3}),
            'quality':forms.Textarea(attrs={'rows':3}),
            'quality_self_review':forms.Textarea(attrs={'rows':3}),
            'accountability':forms.Textarea(attrs={'rows':3}),
            'accountability_self_review':forms.Textarea(attrs={'rows':3}),
        }

class PerformanceReviewAdminForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = ['comments','responsibility_rating','communication_rating','quality_rating','accountability_rating']
        widgets = {
            'comments':forms.Textarea(attrs={'rows':3}),
            'responsibility_rating':forms.NumberInput(attrs={'step':0.1,'min':0,'max':5}),
            'communication_rating':forms.NumberInput(attrs={'step':0.1,'min':0,'max':5}),
            'quality_rating':forms.NumberInput(attrs={'step':0.1,'min':0,'max':5}),
            'accountability_rating':forms.NumberInput(attrs={'step':0.1,'min':0,'max':5}),
        }

        def save(self,commit =True):
            instance = super().save(commit=False)
            if (instance.responsibility_rating and instance.communication_rating and instance.quality_rating and instance.accountability_rating):
                instance.graded = 'GRADED'
            if commit:
                instance.save(
                    update_fields = ['comments','responsibility_rating','communication_rating','quality_rating','accountability_rating','graded']
                )
            return instance

class PerformanceReviewAdminUpdateForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = ['comments','responsibility_rating','communication_rating','quality_rating','accountability_rating']
        widgets = {
            'comments':forms.Textarea(attrs={'rows':3}),
            'responsibility_rating':forms.NumberInput(attrs={'step':0.1,'min':0,'max':5}),
            'communication_rating':forms.NumberInput(attrs={'step':0.1,'min':0,'max':5}),
            'quality_rating':forms.NumberInput(attrs={'step':0.1,'min':0,'max':5}),
            'accountability_rating':forms.NumberInput(attrs={'step':0.1,'min':0,'max':5}),
        }

        def save(self,commit = True):
            instance = super().save(commit=False)
            if (instance.responsibility_rating and instance.communication_rating and instance.quality_rating and instance.accountability_rating):
                instance.graded = 'GRADED'
            if commit:
                instance.save(
                    update_fields = ['graded','comments','responsibility_rating','communication_rating','quality_rating','accountability_rating']
                )
            return instance