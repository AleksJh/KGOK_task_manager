from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    CommentForm,
    DepartmentForm,
    EmailConfigurationForm,
    TaskForm,
    TaskStatusForm,
)
from .models import Department, EmailConfiguration, Task


@login_required
def dashboard(request):
    """Главная страница с аналитикой."""
    if request.user.is_admin:
        # Для администратора показываем статистику по всем службам
        total_tasks = Task.objects.count()
        completed_tasks = Task.objects.filter(status=Task.Status.COMPLETED).count()
        in_progress_tasks = Task.objects.filter(status=Task.Status.IN_PROGRESS).count()
        overdue_tasks = Task.objects.filter(
            ~Q(status=Task.Status.COMPLETED),
            due_date__lt=timezone.now()
        ).count()
        
        # Статистика по службам
        departments = Department.objects.all()
        department_stats = []
        
        for department in departments:
            department_tasks = Task.objects.filter(assigned_to=department)
            stats = {
                'department': department,
                'total': department_tasks.count(),
                'completed': department_tasks.filter(status=Task.Status.COMPLETED).count(),
                'in_progress': department_tasks.filter(status=Task.Status.IN_PROGRESS).count(),
                'overdue': department_tasks.filter(
                    ~Q(status=Task.Status.COMPLETED),
                    due_date__lt=timezone.now()
                ).count(),
            }
            department_stats.append(stats)
        
        context = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'overdue_tasks': overdue_tasks,
            'department_stats': department_stats,
        }
        return render(request, 'tasks/admin_dashboard.html', context)
    else:
        # Для обычного пользователя показываем только его задачи
        department = request.user.department
        if not department:
            messages.error(request, 'У вас нет привязки к службе. Обратитесь к администратору.')
            return redirect('login')
        
        tasks = Task.objects.filter(assigned_to=department)
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status=Task.Status.COMPLETED).count()
        in_progress_tasks = tasks.filter(status=Task.Status.IN_PROGRESS).count()
        overdue_tasks = tasks.filter(
            ~Q(status=Task.Status.COMPLETED),
            due_date__lt=timezone.now()
        ).count()
        
        context = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'overdue_tasks': overdue_tasks,
            'tasks': tasks,
        }
        return render(request, 'tasks/user_dashboard.html', context)


@login_required
def task_list(request):
    """Список всех задач."""
    status_filter = request.GET.get('status', '')
    
    if request.user.is_admin:
        tasks = Task.objects.all()
    else:
        department = request.user.department
        if not department:
            messages.error(request, 'У вас нет привязки к службе. Обратитесь к администратору.')
            return redirect('login')
        tasks = Task.objects.filter(assigned_to=department)
    
    # Применяем фильтр по статусу
    if status_filter == 'completed':
        tasks = tasks.filter(status=Task.Status.COMPLETED)
    elif status_filter == 'in_progress':
        tasks = tasks.filter(status=Task.Status.IN_PROGRESS)
    elif status_filter == 'overdue':
        tasks = tasks.filter(
            ~Q(status=Task.Status.COMPLETED),
            due_date__lt=timezone.now()
        )
    
    context = {
        'tasks': tasks,
        'status_filter': status_filter,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_detail(request, pk):
    """Детальная информация о задаче."""
    task = get_object_or_404(Task, pk=pk)
    
    # Проверяем доступ к задаче
    if not request.user.is_admin and request.user.department != task.assigned_to:
        return HttpResponseForbidden("У вас нет доступа к этой задаче.")
    
    comments = task.comments.all()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        status_form = TaskStatusForm(request.POST, instance=task)
        
        if 'submit_comment' in request.POST and comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен.')
            return redirect('task_detail', pk=task.pk)
        
        if 'submit_status' in request.POST and status_form.is_valid():
            status_form.save()
            messages.success(request, 'Статус задачи обновлен.')
            return redirect('task_detail', pk=task.pk)
    else:
        comment_form = CommentForm()
        status_form = TaskStatusForm(instance=task)
    
    context = {
        'task': task,
        'comments': comments,
        'comment_form': comment_form,
        'status_form': status_form,
    }
    return render(request, 'tasks/task_detail.html', context)


@login_required
def task_create(request):
    """Создание новой задачи."""
    if not request.user.is_admin:
        return HttpResponseForbidden("Только администраторы могут создавать задачи.")
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            messages.success(request, 'Задача успешно создана.')
            return redirect('task_list')
    else:
        form = TaskForm()
    
    context = {
        'form': form,
        'title': 'Создать новую задачу',
    }
    return render(request, 'tasks/task_form.html', context)


@login_required
def task_edit(request, pk):
    """Редактирование задачи."""
    task = get_object_or_404(Task, pk=pk)
    
    if not request.user.is_admin:
        return HttpResponseForbidden("Только администраторы могут редактировать задачи.")
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Задача успешно обновлена.')
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    
    context = {
        'form': form,
        'title': 'Редактировать задачу',
    }
    return render(request, 'tasks/task_form.html', context)


@login_required
def department_list(request):
    """Список всех служб."""
    if not request.user.is_admin:
        return HttpResponseForbidden("Только администраторы имеют доступ к управлению службами.")
    
    departments = Department.objects.all()
    context = {
        'departments': departments,
    }
    return render(request, 'tasks/department_list.html', context)


@login_required
def department_create(request):
    """Создание новой службы."""
    if not request.user.is_admin:
        return HttpResponseForbidden("Только администраторы могут создавать службы.")
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Служба успешно создана.')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    
    context = {
        'form': form,
        'title': 'Создать новую службу',
    }
    return render(request, 'tasks/department_form.html', context)


@login_required
def department_edit(request, pk):
    """Редактирование службы."""
    department = get_object_or_404(Department, pk=pk)
    
    if not request.user.is_admin:
        return HttpResponseForbidden("Только администраторы могут редактировать службы.")
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Служба успешно обновлена.')
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    
    context = {
        'form': form,
        'title': 'Редактировать службу',
    }
    return render(request, 'tasks/department_form.html', context)


@login_required
def email_config(request):
    """Настройка параметров SMTP для отправки email."""
    if not request.user.is_admin:
        return HttpResponseForbidden("Только администраторы имеют доступ к настройкам Email.")
    
    config = EmailConfiguration.objects.first()
    
    if request.method == 'POST':
        if config:
            form = EmailConfigurationForm(request.POST, instance=config)
        else:
            form = EmailConfigurationForm(request.POST)
        
        if form.is_valid():
            # Деактивируем все существующие конфигурации
            EmailConfiguration.objects.update(is_active=False)
            
            # Сохраняем новую конфигурацию как активную
            email_config = form.save(commit=False)
            email_config.is_active = True
            email_config.save()
            
            messages.success(request, 'Настройки Email успешно сохранены.')
            return redirect('email_config')
    else:
        if config:
            form = EmailConfigurationForm(instance=config)
        else:
            form = EmailConfigurationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'tasks/email_config.html', context)