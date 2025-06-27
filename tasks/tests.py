from django.test import TestCase
from django.contrib.auth.models import User
from tasks.models import Task
from django.utils import timezone

class TaskModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='sender', password='pass1234')
        self.user2 = User.objects.create_user(username='receiver', password='pass5678')

    def test_create_task(self):
        task = Task.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            title='Проверить отчёт',
            description='Пожалуйста, проверьте финансовый отчёт за май.',
            is_urgent=True,
            date_created=timezone.now()
        )
        self.assertEqual(task.from_user.username, 'sender')
        self.assertEqual(task.to_user.username, 'receiver')
        self.assertEqual(task.title, 'Проверить отчёт')
        self.assertTrue(task.is_urgent)
        self.assertIsNotNone(task.date_created)

    def test_string_representation(self):
        task = Task(title='Срочная задача')
        self.assertEqual(str(task), 'Срочная задача')
