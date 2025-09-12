from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class AccountFBVTests(TestCase):
    def test_join_get(self):
        resp = self.client.get(reverse('account:join'))
        self.assertEqual(resp.status_code, 200)

    def test_join_post_and_login_logout(self):
        # join
        data = {
            'username': 'user1',
            'password1': 'pass1234AB',
            'password2': 'pass1234AB',
            'name': '유저',
            'email': 'u@e.st',
            'gender': 'M',
        }
        resp = self.client.post(reverse('account:join'), data)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(username='user1').exists())

        # login
        resp = self.client.post(reverse('account:login'), {
            'username': 'user1', 'password': 'pass1234AB'
        })
        self.assertEqual(resp.status_code, 302)

        # logout (POST-only)
        resp = self.client.post(reverse('account:logout'))
        self.assertEqual(resp.status_code, 302)
