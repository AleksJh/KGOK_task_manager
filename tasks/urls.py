from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

urlpatterns = [
    # Аутентификация
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='tasks/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    
    # Дашборд
    path('', views.dashboard, name='dashboard'),
    
    # Задачи
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    
    # Службы
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    
    # Настройки Email
    path('email-config/', views.email_config, name='email_config'),
]