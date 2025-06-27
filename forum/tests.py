from django.test import TestCase
from django.contrib.auth.models import User
from .models import Post, Replies, Section, SectionTheme
from django.utils import timezone

class ReplyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='poster', password='testpass')
        self.section_theme = SectionTheme.objects.create(name='test', priority=1)
        self.section = Section.objects.create(name='test', theme=self.section_theme)
        self.post = Post.objects.create(author=self.user, title='Обсуждение задач', content='Что думаете об этом подходе?', section=self.section)

    def test_create_reply(self):
        reply = Replies.objects.create(
            post=self.post,
            author=self.user,
            reply='Согласен с предложением.',
            date_posted=timezone.now()
        )
        self.assertEqual(reply.post, self.post)
        self.assertEqual(reply.author.username, 'poster')
        self.assertEqual(reply.reply, 'Согласен с предложением.')

    def test_reply_string_representation(self):
        reply = Replies(reply='Хорошо сказано.')
        self.assertEqual(str(reply), 'Хорошо сказано.')
