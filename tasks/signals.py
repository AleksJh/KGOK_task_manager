from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Task, Comment
from .tasks import send_task_notification, send_comment_notification


@receiver(post_save, sender=Task)
def task_post_save(sender, instance, created, **kwargs):
    """Отправка уведомления при создании новой задачи."""
    if created:
        send_task_notification.delay(instance.id)


@receiver(post_save, sender=Comment)
def comment_post_save(sender, instance, created, **kwargs):
    """Отправка уведомления при добавлении комментария к задаче."""
    if created:
        send_comment_notification.delay(instance.id)