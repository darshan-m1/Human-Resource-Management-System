from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import datetime
from django.utils import timezone

# Create your models here.
class Department(models.Model):
    department = models.CharField(max_length=20)
    def __str__(self):
        return self.department

class SingleCEO(models.Manager):
    def create_ceo(self, **kwargs):
        if self.filter(role='CEO').exists():
            raise ValidationError("CEO already exists")
        else:
            return self.create(role='CEO', **kwargs)

class Employee(models.Model):
    objects=SingleCEO()
    ROLE_CHOICES = [
        ('CEO', 'CEO'),
        ('HR', 'HR'),
        ('MANAGER', 'MANAGER'),
        ('TEAM LEAD', 'TEAM LEAD'),
        ('DEVELOPER', 'DEVELOPER'),
        ('TESTER', 'TESTER'),
        ('INTERN', 'INTERN'),
    ]
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    role = models.CharField(choices=ROLE_CHOICES)
    reporting_to = models.ForeignKey('self',null=True,blank=True,on_delete=models.SET_NULL)

    def get_id(self):
        return self.user.id
    
    def __str__(self):
        return self.user.get_full_name()
    
    
class LearningPlan(models.Model):
    Options = [
        ('APPROVED','APPROVED'),
        ('REVIEW','REVIEW'),
        ('REJECTED','REJECTED'),
        ('SUBMITTED','SUBMITTED'),
        ('PENDING','PENDING')
    ]
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE,related_name='learning_plans')
    completed_learning = models.TextField(max_length=250)
    planned_learning = models.TextField(max_length=250)
    status = models.CharField(choices=Options,default='SUBMITTED')
    approved_by = models.ForeignKey(Employee,blank=True,null=True,on_delete=models.SET_NULL,related_name='approved_plans')
    review_note = models.TextField(max_length=50,blank=True,null=True)
    schedule_meeting = models.DateField(null=True,blank=True)
    submitted_at = models.DateField(auto_now=True)
    approved_at = models.DateField(auto_now_add=True,blank=True,null=True)
    end_date = models.DateField(null=True,blank=True,editable=False)
    quarter_date = models.DateField(default=timezone.now)
    
    def get_end_date(self):
        if self.end_date:
            return self.end_date.strftime("%d %b %Y")
        return "Not set"
    
    def save(self, *args, **kwargs):
        if self.quarter_date:
            self.end_date = self.quarter_date + datetime.timedelta(days=90)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.employee.user.get_full_name(), self.schedule_meeting

class PerformanceReview(models.Model):
    options =[
        ('PENDING','PENDING'),
        ('GRADED','GRADED'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,related_name='performance_review')
    responsibilities = models.TextField(max_length=100)
    responsibility_self_review= models.TextField(max_length=100)
    communication= models.TextField(max_length=100)
    communication_self_review = models.TextField(max_length=100)
    quality = models.TextField(max_length=100)
    quality_self_review = models.TextField(max_length=100)
    accountability = models.TextField(max_length=100)
    accountability_self_review = models.TextField(max_length=100)
    comments = models.TextField(max_length=100,blank=True,null=True)
    commented_by = models.ForeignKey(Employee,on_delete=models.CASCADE,blank=True,null=True,related_name='performance_grader')
    responsibility_rating = models.DecimalField(max_digits=3,decimal_places=1,blank=True,null=True)
    communication_rating = models.DecimalField(max_digits=3,decimal_places=1,blank=True,null=True)
    quality_rating = models.DecimalField(max_digits=3,decimal_places=1,blank=True,null=True)
    accountability_rating = models.DecimalField(max_digits=3,decimal_places=1,blank=True,null=True)
    graded = models.CharField(choices=options,default='PENDING')

    @property
    def average_score(self):
        ratings = [
            self.responsibility_rating,
            self.communication_rating,
            self.quality_rating,
            self.accountability_rating
        ]
        
        valid_ratings = [r for r in ratings if r is not None]
        if valid_ratings:
            return sum(valid_ratings) / len(valid_ratings)
        return None

    def save(self, *args, **kwargs):
        if (self.responsibility_rating is not None and 
            self.communication_rating is not None and 
            self.quality_rating is not None and 
            self.accountability_rating is not None):
            self.graded = 'GRADED'
        else:
            self.graded = 'PENDING'
        if self.comments and self.comments.strip() and not self.commented_by:
            pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.employee.user.get_full_name(), self.graded