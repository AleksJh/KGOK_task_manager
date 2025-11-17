from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Comment, EmailConfiguration, Task


def get_email_config():
    """Получение активной конфигурации Email."""
    config = EmailConfiguration.objects.filter(is_active=True).first()
    if config:
        return {
            'host': config.smtp_host,
            'port': config.smtp_port,
            'username': config.smtp_user,
            'password': config.smtp_password,
            'use_tls': config.use_tls,
            'from_email': config.from_email,
        }
    return None


@shared_task
def send_task_notification(task_id):
    """Отправка уведомления о новой задаче."""
    try:
        task = Task.objects.get(id=task_id)
        recipient_email = task.assigned_to.email
        
        # Формирование сообщения
        subject = f'Новая задача: {task.title}'
        html_message = render_to_string('tasks/email/task_notification.html', {
            'task': task,
        })
        plain_message = strip_tags(html_message)
        
        # Отправка email
        email_config = get_email_config()
        from_email = email_config['from_email'] if email_config else settings.DEFAULT_FROM_EMAIL
        
        send_mail(
            subject,
            plain_message,
            from_email,
            [recipient_email],
            html_message=html_message,
        )
        
        return f'Уведомление о задаче {task_id} успешно отправлено на {recipient_email}'
    except Task.DoesNotExist:
        return f'Задача с ID {task_id} не найдена'
    except Exception as e:
        return f'Ошибка при отправке уведомления о задаче: {str(e)}'


@shared_task
def send_comment_notification(comment_id):
    """Отправка уведомления о новом комментарии."""
    try:
        comment = Comment.objects.get(id=comment_id)
        task = comment.task
        
        # Получаем список получателей (назначенная служба и создатель задачи)
        recipients = [task.assigned_to.email]
        if task.assigned_by.email not in recipients:
            recipients.append(task.assigned_by.email)
        
        # Исключаем автора комментария из получателей
        if comment.user.email in recipients:
            recipients.remove(comment.user.email)
        
        if not recipients:
            return f'Нет получателей для уведомления о комментарии {comment_id}'
        
        # Формирование сообщения
        subject = f'Новый комментарий к задаче: {task.title}'
        html_message = render_to_string('tasks/email/comment_notification.html', {
            'comment': comment,
            'task': task,
        })
        plain_message = strip_tags(html_message)
        
        # Отправка email
        email_config = get_email_config()
        from_email = email_config['from_email'] if email_config else settings.DEFAULT_FROM_EMAIL
        
        send_mail(
            subject,
            plain_message,
            from_email,
            recipients,
            html_message=html_message,
        )
        
        recipients_str = ", ".join(recipients)
        return f'Уведомление о комментарии {comment_id} успешно отправлено на {recipients_str}'
    except Comment.DoesNotExist:
        return f'Комментарий с ID {comment_id} не найден'
    except Exception as e:
        return f'Ошибка при отправке уведомления о комментарии: {str(e)}'