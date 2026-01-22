# 🏢 HR Management System (HRMS)
A comprehensive Human Resource Management System built with Django, designed to streamline employee management, performance tracking, and HR operations.

https://img.shields.io/badge/Django-4.2-green

https://img.shields.io/badge/Bootstrap-5.0-blue

https://img.shields.io/badge/License-MIT-yellow

# ✨ Features
## 👥 Employee Management
Employee Profiles - Complete employee information management

Department Management - Organize employees by departments

Reporting Structure - Manager-subordinate hierarchy

Role-based Access - CEO, HR, Manager, Employee roles

## 📊 Performance Management
Quarterly Reviews - Performance evaluation system

360° Feedback - Multi-rater assessment

Grading System - Automated scoring and grading

Review History - Track performance over time

## 📚 Learning & Development
Learning Plans - Create and assign training programs

Skill Tracking - Monitor employee skill development

Training Modules - Organized learning materials

Progress Tracking - Monitor completion status

## 📧 Notifications & Communication
Email Automation - Welcome emails, review reminders

Real-time Alerts - System notifications

Approval Workflows - Manager approvals for requests

Status Updates - Automatic notifications

## 🚀 Quick Start
### Prerequisites
Python 3.8+

Django 4.2+

PostgreSQL/MySQL (optional)

Virtual Environment

## Installation
1. Clone the repository
   ```bash
   git clone https://github.com/darshan-m1/Human-Resource-Management-System ```

2. Create virtual environment
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On Mac/Linux
    source venv/bin/activate```

3. Install dependencies
   ```bash
   pip install django django-filter```

4. Configure environment variables

Create .env file:
    ```
    SECRET_KEY=your-secret-key-here
    DEBUG=True
    DATABASE_URL=sqlite:///db.sqlite3
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587```

6. Run migrations
   ```
   python manage.py makemigrations
   python manage.py migrate

7. Create superuser
   ```bash
   python manage.py createsuperuser

8. Run Server
   ```bash
   python manage.py runserver

Visit: http://127.0.0.1:8000/
