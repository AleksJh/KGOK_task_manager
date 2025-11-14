from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from tasks.models import Department, Task
from tasks.tests.test_models import DepartmentFactory, UserFactory, TaskFactory


User = get_user_model()


class ViewsTestCase(TestCase):
    def setUp(self):
        # Создаем администратора
        self.admin_user = UserFactory(
            username='admin',
            email='admin@kgok.ru',
            is_admin=True,
            is_staff=True,
            is_superuser=True,
            department=None
        )
        self.admin_user.set_password('adminpass')
        self.admin_user.save()

        # Создаем службу и пользователя службы
        self.department = DepartmentFactory(
            name='Тестовая служба',
            email='test@kgok.ru'
        )
        self.service_user = UserFactory(
            username='service',
            email='service@kgok.ru',
            is_admin=False,
            department=self.department
        )
        self.service_user.set_password('servicepass')
        self.service_user.save()

        # Создаем задачи
        self.task = TaskFactory(
            title='Тестовая задача',
            description='Описание тестовой задачи',
            status=Task.Status.NEW,
            assigned_to=self.department,
            assigned_by=self.admin_user,
        )

        # Создаем клиенты
        self.client = Client()
        self.admin_client = Client()
        self.admin_client.login(username='admin', password='adminpass')
        self.service_client = Client()
        self.service_client.login(username='service', password='servicepass')


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client = Client()

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_view_post_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)

    def test_login_view_post_success_with_email(self):
        response = self.client.post(reverse('login'), {
            'username': 'test@example.com',
            'password': 'testpassword'
        })
        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)

    def test_login_view_post_failure(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')


class DashboardViewTest(ViewsTestCase):
    def test_dashboard_view_admin(self):
        response = self.admin_client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/dashboard.html')
        self.assertIn('departments', response.context)
        self.assertIn('tasks_by_status', response.context)

    def test_dashboard_view_service(self):
        response = self.service_client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/dashboard.html')
        self.assertIn('tasks', response.context)

    def test_dashboard_view_unauthenticated(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")


class TaskListViewTest(ViewsTestCase):
    def test_task_list_view_admin(self):
        response = self.admin_client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_list.html')
        self.assertIn('tasks', response.context)

    def test_task_list_view_service(self):
        response = self.service_client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_list.html')
        self.assertIn('tasks', response.context)

    def test_task_list_view_filter(self):
        # Создаем задачи с разными статусами
        TaskFactory(status=Task.Status.NEW, assigned_to=self.department)
        TaskFactory(status=Task.Status.IN_PROGRESS, assigned_to=self.department)
        TaskFactory(status=Task.Status.COMPLETED, assigned_to=self.department)

        # Проверяем фильтр по статусу NEW
        response = self.admin_client.get(f"{reverse('task_list')}?status={Task.Status.NEW}")
        self.assertEqual(response.status_code, 200)
        tasks = response.context['tasks']
        for task in tasks:
            self.assertEqual(task.status, Task.Status.NEW)


class TaskDetailViewTest(ViewsTestCase):
    def test_task_detail_view(self):
        response = self.admin_client.get(reverse('task_detail', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_detail.html')
        self.assertEqual(response.context['task'], self.task)
        self.assertIn('status_form', response.context)
        self.assertIn('comment_form', response.context)

    def test_task_detail_view_post_status(self):
        response = self.admin_client.post(
            reverse('task_detail', args=[self.task.id]),
            {'status': Task.Status.IN_PROGRESS, 'form_type': 'status'}
        )
        self.assertRedirects(response, reverse('task_detail', args=[self.task.id]))
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.IN_PROGRESS)

    def test_task_detail_view_post_comment(self):
        response = self.admin_client.post(
            reverse('task_detail', args=[self.task.id]),
            {'content': 'Тестовый комментарий', 'form_type': 'comment'}
        )
        self.assertRedirects(response, reverse('task_detail', args=[self.task.id]))
        self.assertEqual(self.task.comments.count(), 1)
        self.assertEqual(self.task.comments.first().content, 'Тестовый комментарий')


class TaskCreateViewTest(ViewsTestCase):
    def test_task_create_view_admin_get(self):
        response = self.admin_client.get(reverse('task_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_form.html')
        self.assertIn('form', response.context)

    def test_task_create_view_service_get(self):
        # Обычные пользователи не должны иметь доступ к созданию задач
        response = self.service_client.get(reverse('task_create'))
        self.assertEqual(response.status_code, 403)

    def test_task_create_view_admin_post(self):
        task_count = Task.objects.count()
        response = self.admin_client.post(reverse('task_create'), {
            'title': 'Новая задача',
            'description': 'Описание новой задачи',
            'status': Task.Status.NEW,
            'assigned_to': self.department.id,
            'due_date': '2023-12-31T12:00'
        })
        self.assertEqual(Task.objects.count(), task_count + 1)
        new_task = Task.objects.latest('id')
        self.assertEqual(new_task.title, 'Новая задача')
        self.assertEqual(new_task.assigned_by, self.admin_user)
        self.assertRedirects(response, reverse('task_detail', args=[new_task.id]))


class DepartmentListViewTest(ViewsTestCase):
    def test_department_list_view_admin(self):
        response = self.admin_client.get(reverse('department_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/department_list.html')
        self.assertIn('departments', response.context)

    def test_department_list_view_service(self):
        # Обычные пользователи не должны иметь доступ к списку служб
        response = self.service_client.get(reverse('department_list'))
        self.assertEqual(response.status_code, 403)


class DepartmentCreateViewTest(ViewsTestCase):
    def test_department_create_view_admin_get(self):
        response = self.admin_client.get(reverse('department_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/department_form.html')
        self.assertIn('form', response.context)

    def test_department_create_view_service_get(self):
        # Обычные пользователи не должны иметь доступ к созданию служб
        response = self.service_client.get(reverse('department_create'))
        self.assertEqual(response.status_code, 403)

    def test_department_create_view_admin_post(self):
        department_count = Department.objects.count()
        response = self.admin_client.post(reverse('department_create'), {
            'name': 'Новая служба',
            'email': 'new@kgok.ru'
        })
        self.assertEqual(Department.objects.count(), department_count + 1)
        new_department = Department.objects.latest('id')
        self.assertEqual(new_department.name, 'Новая служба')
        self.assertRedirects(response, reverse('department_list'))