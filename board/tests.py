from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Post, Category


class BoardFBVTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester', password='pass1234', name='Tester', email='t@e.st', gender='M'
        )
        self.category = Category.objects.create(category_name='일반')

    def test_list_view(self):
        url = reverse('board:list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_create_requires_login(self):
        url = reverse('board:create')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)  # redirect to login

    def test_create_update_delete_flow(self):
        self.client.login(username='tester', password='pass1234')
        # create
        create_url = reverse('board:create')
        data = {
            'title': '제목',
            'content': '내용',
            'category': self.category.pk,
        }
        resp = self.client.post(create_url, data)
        self.assertEqual(resp.status_code, 302)
        post = Post.objects.first()
        self.assertIsNotNone(post)
        # detail
        detail_url = reverse('board:detail', args=[post.pk])
        resp = self.client.get(detail_url)
        self.assertContains(resp, '제목')
        # update
        update_url = reverse('board:update', args=[post.pk])
        resp = self.client.post(update_url, {**data, 'title': '제목2'})
        self.assertEqual(resp.status_code, 302)
        post.refresh_from_db()
        self.assertEqual(post.title, '제목2')
        # delete (GET as in current behavior)
        delete_url = reverse('board:delete', args=[post.pk])
        resp = self.client.get(delete_url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Post.objects.count(), 0)

    def test_comments_crud(self):
        self.client.login(username='tester', password='pass1234')
        post = Post.objects.create(title='t', content='c', category=self.category, writer=self.user)
        # create
        url = reverse('board:comment_create', args=[post.pk])
        resp = self.client.post(url, {'content': 'hi'})
        self.assertEqual(resp.status_code, 200)
        cid = post.comments.first().pk
        # update
        url_u = reverse('board:comment_update', args=[cid])
        resp = self.client.post(url_u, {'content': 'hello'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('hello', resp.json().get('html', ''))
        # delete
        url_d = reverse('board:comment_delete', args=[cid])
        resp = self.client.post(url_d)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(post.comments.count(), 0)
