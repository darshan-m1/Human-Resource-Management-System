from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.db import transaction
from .models import PerformanceReview, Employee, LearningPlan

@receiver(post_save,sender=Employee)
def send_welcome_email(sender,instance,created, **kwargs):
    if created and instance.user.email:
        transaction.on_commit(lambda:send_mail('Happy Onboarding',
            f''' 
                Welcome {instance.user.get_full_name()},

                You are now a part of Enkefalos

                We are glad to have you

                Your Details:
                Employee ID: ENK00{instance.user.id}
                Role: {instance.role}
                Department: {instance.department}

                Best Regards,
                HR Team''',
                'hr@enkefalos.com',
                [instance.user.email],
                fail_silently=True
                        ))
        
def performance_grade_email(performance):
    try:
        if not performance.employee:
            return
            
        if not performance.employee.user:
            return
            
        if not performance.employee.user.email:
            return
            
        
        subject = 'Your Performance Review is Ready'
        action = 'view'

        message = f'''
        Hello, {performance.employee.user.get_full_name()},
        
        Your performance review has been graded.
        
        Overall Score: { performance.average_score} / 5.0
        
        Login to {action} your grades.
        
        Best Regards,
        {performance.commented_by.user.get_full_name() if performance.commented_by else 'HR'}'''
        send_mail(
            subject = subject,
            message=message,
            from_email='hr@enkefalos.com',
            recipient_list=[performance.employee.user.email],
            fail_silently=False
        )
        print(" Email sent successfully!")
        
    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()

@receiver(post_save, sender=PerformanceReview)
def send_performance_email(sender, instance, created, **kwargs):
    if not created:
        transaction.on_commit(lambda: performance_grade_email(instance))