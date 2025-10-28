from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _

from .models import User, Task, Department, Comment, EmailConfiguration


class CustomAuthenticationForm(AuthenticationForm):
    """Кастомная форма аутентификации."""
    username = forms.CharField(label=_('Email'), widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label=_('Пароль'), widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserForm(UserCreationForm):
    """Форма для создания пользователя."""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_admin', 'department', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_admin': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }


class DepartmentForm(forms.ModelForm):
    """Форма для создания и редактирования службы."""
    class Meta:
        model = Department
        fields = ('name', 'email')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class TaskForm(forms.ModelForm):
    """Форма для создания и редактирования задачи."""
    due_date = forms.DateTimeField(
        label=_('Крайний срок'),
        widget=forms.DateTimeInput(
            attrs={'class': 'form-control', 'type': 'datetime-local'}
        ),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Task
        fields = ('title', 'description', 'status', 'assigned_to', 'due_date')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }


class TaskStatusForm(forms.ModelForm):
    """Форма для обновления статуса задачи."""
    class Meta:
        model = Task
        fields = ('status',)
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class CommentForm(forms.ModelForm):
    """Форма для добавления комментария к задаче."""
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Добавить комментарий...'}),
        }
        labels = {
            'content': '',
        }


class EmailConfigurationForm(forms.ModelForm):
    """Форма для настройки параметров SMTP."""
    class Meta:
        model = EmailConfiguration
        fields = ('smtp_host', 'smtp_port', 'smtp_user', 'smtp_password', 'use_tls', 'from_email')
        widgets = {
            'smtp_host': forms.TextInput(attrs={'class': 'form-control'}),
            'smtp_port': forms.NumberInput(attrs={'class': 'form-control'}),
            'smtp_user': forms.TextInput(attrs={'class': 'form-control'}),
            'smtp_password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'use_tls': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'from_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }