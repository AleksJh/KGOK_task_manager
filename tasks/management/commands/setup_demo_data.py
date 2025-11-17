import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from tasks.models import Department, EmailConfiguration, Task, User


class Command(BaseCommand):
    help = 'Инициализирует демо-данные для системы управления задачами'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Начало инициализации демо-данных...')

        # Создание служб
        self.stdout.write('Создание служб...')
        departments = {
            'geology': Department.objects.create(
                name='Геологическая служба',
                email='geology@kgok.ru',
            ),
            'geomech': Department.objects.create(
                name='Геомеханический отдел',
                email='geomech@kgok.ru',
            ),
            'survey': Department.objects.create(
                name='Маркшейдерская служба',
                email='survey@kgok.ru',
            ),
            'drilling': Department.objects.create(
                name='Буровзрывной отдел',
                email='drilling@kgok.ru',
            ),
        }

        # Создание администратора
        self.stdout.write('Создание администратора...')
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@kgok.ru',
            password='adminpass',
            first_name='Администратор',
            last_name='Системы',
            is_admin=True,
            is_staff=True,
            is_superuser=True,
        )

        # Создание пользователей для служб
        self.stdout.write('Создание пользователей для служб...')
        User.objects.create_user(
            username='geology',
            email='geology@kgok.ru',
            password='servicepass',
            first_name='Геологическая',
            last_name='Служба',
            department=departments['geology'],
        )
        User.objects.create_user(
            username='geomech',
            email='geomech@kgok.ru',
            password='servicepass',
            first_name='Геомеханический',
            last_name='Отдел',
            department=departments['geomech'],
        )
        User.objects.create_user(
            username='survey',
            email='survey@kgok.ru',
            password='servicepass',
            first_name='Маркшейдерская',
            last_name='Служба',
            department=departments['survey'],
        )
        User.objects.create_user(
            username='drilling',
            email='drilling@kgok.ru',
            password='servicepass',
            first_name='Буровзрывной',
            last_name='Отдел',
            department=departments['drilling'],
        )

        # Создание демо-задач
        self.stdout.write('Создание демо-задач...')
        now = timezone.now()

        # Задача 1: Выполненная задача для геологической службы
        Task.objects.create(
            title='Подготовить геологический отчет',
            description=(
                'Необходимо подготовить квартальный отчет по геологическим изысканиям. '
                'Включить данные по всем скважинам за последние 3 месяца.'
            ),
            status=Task.Status.COMPLETED,
            assigned_to=departments['geology'],
            assigned_by=admin_user,
            due_date=now + datetime.timedelta(days=7),
            created_at=now - datetime.timedelta(days=10),
        )

        # Задача 2: Задача в работе для геомеханического отдела
        Task.objects.create(
            title='Провести анализ устойчивости',
            description=(
                'Анализ устойчивости бортов карьера в зоне A. '
                'Особое внимание уделить северному борту.'
            ),
            status=Task.Status.IN_PROGRESS,
            assigned_to=departments['geomech'],
            assigned_by=admin_user,
            due_date=now + datetime.timedelta(days=5),
            created_at=now - datetime.timedelta(days=3),
        )

        # Задача 3: Ожидающая задача для маркшейдерской службы
        Task.objects.create(
            title='Маркшейдерская съемка',
            description=(
                'Провести плановую съемку участка №3. '
                'Необходимо определить точные координаты и высотные отметки.'
            ),
            status=Task.Status.NEW,
            assigned_to=departments['survey'],
            assigned_by=admin_user,
            due_date=now + datetime.timedelta(days=14),
            created_at=now - datetime.timedelta(days=1),
        )

        # Задача 4: Просроченная задача для буровзрывного отдела
        Task.objects.create(
            title='Подготовить план БВР',
            description=(
                'Разработать план буровзрывных работ для участка №2. '
                'Учесть близость водоносного горизонта.'
            ),
            status=Task.Status.NEW,
            assigned_to=departments['drilling'],
            assigned_by=admin_user,
            due_date=now - datetime.timedelta(days=2),
            created_at=now - datetime.timedelta(days=7),
        )

        # Задача 5: Отложенная задача для геологической службы
        Task.objects.create(
            title='Анализ керновых проб',
            description=(
                'Провести детальный анализ керновых проб с участка №5. '
                'Определить содержание полезных компонентов.'
            ),
            status=Task.Status.POSTPONED,
            assigned_to=departments['geology'],
            assigned_by=admin_user,
            due_date=now + datetime.timedelta(days=10),
            created_at=now - datetime.timedelta(days=5),
        )

        # Задача 6: Еще одна задача в работе
        Task.objects.create(
            title='Обновление цифровой модели',
            description=(
                'Обновить цифровую модель месторождения с учетом данных '
                'последних разведочных скважин.'
            ),
            status=Task.Status.IN_PROGRESS,
            assigned_to=departments['survey'],
            assigned_by=admin_user,
            due_date=now + datetime.timedelta(days=3),
            created_at=now - datetime.timedelta(days=4),
        )

        # Создание настроек Email
        self.stdout.write('Создание настроек Email...')
        EmailConfiguration.objects.create(
            smtp_host='smtp.gmail.com',
            smtp_port=587,
            smtp_user='noreply@kapangok.kz',
            smtp_password='your-email-password',
            use_tls=True,
            from_email='noreply@kapangok.kz',
            is_active=True,
        )

        self.stdout.write(self.style.SUCCESS('Демо-данные успешно инициализированы!'))
        self.stdout.write(self.style.SUCCESS('Администратор: admin@kgok.ru / adminpass'))
        self.stdout.write(
            self.style.SUCCESS(
                'Службы: geology@kgok.ru, geomech@kgok.ru, '
                'survey@kgok.ru, drilling@kgok.ru / servicepass'
            )
        )