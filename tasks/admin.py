from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Comment, Department, EmailConfiguration, Task, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_admin', 'department')
    list_filter = ('is_admin', 'department')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
        (
            'Разрешения',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'is_admin',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        ('Служба', {'fields': ('department',)}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_admin', 'department'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'assigned_to', 'assigned_by', 'due_date', 'is_overdue')
    list_filter = ('status', 'assigned_to', 'assigned_by')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'created_at')
    list_filter = ('task', 'user')
    search_fields = ('content',)
    date_hierarchy = 'created_at'


@admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ('smtp_host', 'smtp_port', 'smtp_user', 'from_email', 'is_active')
    list_filter = ('is_active', 'use_tls')