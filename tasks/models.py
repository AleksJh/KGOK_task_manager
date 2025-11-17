from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Department(models.Model):
    """Модель для представления службы в системе."""
    name = models.CharField(_('Название службы'), max_length=100)
    email = models.EmailField(_('Email для уведомлений'), unique=True)

    class Meta:
        verbose_name = _('Служба')
        verbose_name_plural = _('Службы')

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Расширенная модель пользователя с привязкой к службе."""
    is_admin = models.BooleanField(_('Администратор'), default=False,
                                  help_text=_('Отдел горного планирования'))
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name=_('Служба'),
        related_name='users',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return f"{self.username} ({self.department.name if self.department else 'Без службы'})"


class Task(models.Model):
    """Модель задачи в системе."""
    class Status(models.TextChoices):
        NEW = 'new', _('Новая')
        IN_PROGRESS = 'in_progress', _('В Работе')
        COMPLETED = 'completed', _('Выполнена')
        POSTPONED = 'postponed', _('Отложена')

    title = models.CharField(_('Название'), max_length=200)
    description = models.TextField(_('Описание'))
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    assigned_to = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name=_('Назначена службе'),
        related_name='assigned_tasks',
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Назначена пользователем'),
        related_name='created_tasks',
    )
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    due_date = models.DateTimeField(_('Крайний срок'))

    class Meta:
        verbose_name = _('Задача')
        verbose_name_plural = _('Задачи')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """Проверяет, просрочена ли задача."""
        return self.status != self.Status.COMPLETED and self.due_date < timezone.now()


class Comment(models.Model):
    """Модель комментария к задаче."""
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        verbose_name=_('Задача'),
        related_name='comments',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        related_name='comments',
    )
    content = models.TextField(_('Содержание'))
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)

    class Meta:
        verbose_name = _('Комментарий')
        verbose_name_plural = _('Комментарии')
        ordering = ['created_at']

    def __str__(self):
        return f"Комментарий от {self.user.username} к задаче {self.task.title}"


class EmailConfiguration(models.Model):
    """Модель для хранения настроек SMTP сервера."""
    smtp_host = models.CharField(_('SMTP сервер'), max_length=100)
    smtp_port = models.IntegerField(_('Порт'))
    smtp_user = models.CharField(_('Логин SMTP'), max_length=100)
    smtp_password = models.CharField(_('Пароль SMTP'), max_length=100)
    use_tls = models.BooleanField(_('Использовать TLS'), default=True)
    from_email = models.EmailField(_('Email отправителя'))
    is_active = models.BooleanField(_('Активно'), default=True)

    class Meta:
        verbose_name = _('Настройка Email')
        verbose_name_plural = _('Настройки Email')

    def __str__(self):
        return f"SMTP: {self.smtp_host}:{self.smtp_port}"