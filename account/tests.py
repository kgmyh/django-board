"""
account/tests.py

이 파일은 회원가입/로그인/로그아웃 FBV가 기대대로 동작하는지 검증하는 테스트를 담고 있습니다.

핵심 포인트 요약
- 회원가입(join): GET은 폼 화면을 200 OK로 보여주고, POST는 유효한 데이터로 사용자 생성 후 302 리다이렉트됩니다.
- 로그인(login): AuthenticationForm을 활용하여 POST로 인증하고, 성공 시 302 리다이렉트됩니다.
- 로그아웃(logout): 보안상 POST 전용이며, 성공 시 302 리다이렉트됩니다.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class AccountFBVTests(TestCase):
    """계정 관련 FBV의 기본 시나리오 검증"""

    def test_join_get(self):
        """GET /account/join: 가입 폼 화면이 잘 렌더링되는지 (200 OK) 확인합니다."""
        resp = self.client.get(reverse('account:join'))
        self.assertEqual(resp.status_code, 200)

    def test_join_post_and_login_logout(self):
        """
        가입 → 로그인 → 로그아웃의 기본 플로우를 검증합니다.
        - 가입: 유효한 폼 데이터로 POST 시 사용자 생성 및 302 리다이렉트
        - 로그인: 생성한 계정으로 POST 인증 후 302 리다이렉트
        - 로그아웃: POST 전용 엔드포인트로 302 리다이렉트
        """
        # 1) 가입 (POST)
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

        # 2) 로그인 (POST)
        resp = self.client.post(reverse('account:login'), {
            'username': 'user1', 'password': 'pass1234AB'
        })
        self.assertEqual(resp.status_code, 302)

        # 3) 로그아웃 (POST-only)
        resp = self.client.post(reverse('account:logout'))
        self.assertEqual(resp.status_code, 302)
