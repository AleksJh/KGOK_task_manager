from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from tasks.models import Comment, Department, EmailConfiguration, Task, User


class DepartmentFactory(DjangoModelFactory):
    class Meta:
        model = Department

    name = Faker('company')
    email = Faker('email')


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Faker('user_name')
    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    is_admin = False
    department = SubFactory(DepartmentFactory)


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    title = Faker('sentence')
    description = Faker('paragraph')
    status = Task.Status.NEW
    assigned_to = SubFactory(DepartmentFactory)
    assigned_by = SubFactory(UserFactory)
    due_date = Faker('future_date')


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    task = SubFactory(TaskFactory)
    user = SubFactory(UserFactory)
    content = Faker('paragraph')


class EmailConfigurationFactory(DjangoModelFactory):
    class Meta:
        model = EmailConfiguration

    smtp_host = 'smtp.example.com'
    smtp_port = 587
    smtp_user = 'user@example.com'
    smtp_password = 'password'
    use_tls = True
    from_email = 'noreply@example.com'
    is_active = True


class DepartmentModelTest(TestCase):
    def test_department_creation(self):
        department = DepartmentFactory()
        self.assertIsNotNone(department.id)
        self.assertIsNotNone(department.name)
        self.assertIsNotNone(department.email)

    def test_department_str(self):
        department = DepartmentFactory(name='Тестовая служба')
        self.assertEqual(str(department), 'Тестовая служба')


class UserModelTest(TestCase):
    def test_user_creation(self):
        user = UserFactory()
        self.assertIsNotNone(user.id)
        self.assertIsNotNone(user.username)
        self.assertIsNotNone(user.email)
        self.assertFalse(user.is_admin)
        self.assertIsNotNone(user.department)

    def test_admin_user_creation(self):
        admin = UserFactory(is_admin=True, department=None)
        self.assertTrue(admin.is_admin)
        self.assertIsNone(admin.department)


class TaskModelTest(TestCase):
    def test_task_creation(self):
        task = TaskFactory()
        self.assertIsNotNone(task.id)
        self.assertIsNotNone(task.title)
        self.assertIsNotNone(task.description)
        self.assertEqual(task.status, Task.Status.NEW)
        self.assertIsNotNone(task.assigned_to)
        self.assertIsNotNone(task.assigned_by)
        self.assertIsNotNone(task.due_date)

    def test_task_str(self):
        task = TaskFactory(title='Тестовая задача')
        self.assertEqual(str(task), 'Тестовая задача')

    def test_is_overdue_property(self):
        # Создаем задачу с прошедшим сроком
        past_due_task = TaskFactory(
            due_date=timezone.now() - timedelta(days=1),
            status=Task.Status.NEW
        )
        self.assertTrue(past_due_task.is_overdue)

        # Создаем задачу с будущим сроком
        future_due_task = TaskFactory(
            due_date=timezone.now() + timedelta(days=1),
            status=Task.Status.NEW
        )
        self.assertFalse(future_due_task.is_overdue)

        # Создаем выполненную задачу с прошедшим сроком
        completed_task = TaskFactory(
            due_date=timezone.now() - timedelta(days=1),
            status=Task.Status.COMPLETED
        )
        self.assertFalse(completed_task.is_overdue)


class CommentModelTest(TestCase):
    def test_comment_creation(self):
        comment = CommentFactory()
        self.assertIsNotNone(comment.id)
        self.assertIsNotNone(comment.task)
        self.assertIsNotNone(comment.user)
        self.assertIsNotNone(comment.content)
        self.assertIsNotNone(comment.created_at)

    def test_comment_str(self):
        task = TaskFactory(title='Тестовая задача')
        user = UserFactory(username='testuser')
        comment = CommentFactory(task=task, user=user)
        self.assertEqual(str(comment), 'Комментарий к задаче "Тестовая задача" от testuser')


class EmailConfigurationModelTest(TestCase):
    def test_email_configuration_creation(self):
        config = EmailConfigurationFactory()
        self.assertIsNotNone(config.id)
        self.assertEqual(config.smtp_host, 'smtp.example.com')
        self.assertEqual(config.smtp_port, 587)
        self.assertEqual(config.smtp_user, 'user@example.com')
        self.assertEqual(config.smtp_password, 'password')
        self.assertTrue(config.use_tls)
        self.assertEqual(config.from_email, 'noreply@example.com')
        self.assertTrue(config.is_active)

    def test_email_configuration_str(self):
        config = EmailConfigurationFactory(smtp_host='smtp.test.com')
        self.assertEqual(str(config), 'Настройки Email (smtp.test.com)')