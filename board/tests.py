"""
board/tests.py

이 파일은 게시판(Board) 앱의 함수 기반 뷰(FBV)가 정상 동작하는지 확인하는 단위 테스트를 담고 있습니다.

핵심 포인트 요약
- Django TestCase는 매 테스트를 트랜잭션으로 감싸고, 별도의 테스트 데이터베이스를 사용합니다.
- self.client는 Django의 테스트 클라이언트로, HTTP 요청(get/post 등)을 시뮬레이션합니다.
- reverse('app_name:view_name')는 URL 하드코딩을 피하고, urlpattern의 name으로 주소를 역으로 생성합니다.
- assertEqual/Contains 등 단언(assert) 메서드로 응답 상태 코드나 내용, DB 상태를 검증합니다.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Post, Category


class BoardFBVTests(TestCase):
    """게시판 FBV들의 기본 플로우를 검증하는 테스트 모음입니다."""

    def setUp(self):
        """
        매 테스트 실행 전에 기본 사용자와 카테고리를 하나씩 생성합니다.
        - setUp은 각 테스트 케이스(method)마다 새로 수행되며, 테스트 간 상태가 공유되지 않습니다.
        """
        self.user = get_user_model().objects.create_user(
            username='tester', password='pass1234', name='Tester', email='t@e.st', gender='M'
        )
        self.category = Category.objects.create(category_name='일반')

    def test_list_view(self):
        """
        글 목록 페이지가 정상적으로 200 OK를 반환하는지 확인합니다.
        - 로그인은 필요하지 않은 공개 페이지이므로, 인증 없이 접근합니다.
        """
        url = reverse('board:list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_create_requires_login(self):
        """
        글 작성 페이지는 로그인한 사용자만 접근할 수 있습니다.
        - 비로그인 상태에서 접근 시 로그인 페이지로 302 리다이렉트되는지 확인합니다.
        """
        url = reverse('board:create')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)  # LOGIN_URL로 리다이렉트 기대

    def test_create_update_delete_flow(self):
        """
        글 생성→상세조회→수정→삭제의 전체 플로우를 검증합니다.
        - client.login(...) 으로 세션 기반 로그인을 시뮬레이션합니다.
        - 생성/수정 요청은 POST로 보내며, 성공 시 302 리다이렉트가 기대됩니다.
        - 삭제는 현재 동작상 GET으로 처리하므로 GET 요청 후 목록으로 302 리다이렉트를 기대합니다.
        """
        # 1) 로그인
        self.client.login(username='tester', password='pass1234')

        # 2) 생성 (POST)
        create_url = reverse('board:create')
        data = {
            'title': '제목',
            'content': '내용',
            'category': self.category.pk,
        }
        resp = self.client.post(create_url, data)
        self.assertEqual(resp.status_code, 302)  # 생성 후 상세로 리다이렉트
        post = Post.objects.first()
        self.assertIsNotNone(post)

        # 3) 상세 조회 (GET)
        detail_url = reverse('board:detail', args=[post.pk])
        resp = self.client.get(detail_url)
        self.assertContains(resp, '제목')  # 페이지 내용에 새 제목이 포함되었는지 확인

        # 4) 수정 (POST)
        update_url = reverse('board:update', args=[post.pk])
        resp = self.client.post(update_url, {**data, 'title': '제목2'})
        self.assertEqual(resp.status_code, 302)
        post.refresh_from_db()
        self.assertEqual(post.title, '제목2')

        # 5) 삭제 (GET)
        delete_url = reverse('board:delete', args=[post.pk])
        resp = self.client.get(delete_url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Post.objects.count(), 0)

    def test_comments_crud(self):
        """
        댓글의 생성/수정/삭제 AJAX 엔드포인트를 검증합니다.
        - 댓글 API는 로그인 필요 + POST 전용입니다.
        - 응답은 JSON이며, 성공 시 ok=True와 일부 HTML 스니펫을 반환합니다.
        """
        self.client.login(username='tester', password='pass1234')

        # 테스트용 게시글 생성
        post = Post.objects.create(title='t', content='c', category=self.category, writer=self.user)

        # 1) 생성
        url = reverse('board:comment_create', args=[post.pk])
        resp = self.client.post(url, {'content': 'hi'})
        self.assertEqual(resp.status_code, 200)
        cid = post.comments.first().pk

        # 2) 수정
        url_u = reverse('board:comment_update', args=[cid])
        resp = self.client.post(url_u, {'content': 'hello'})
        self.assertEqual(resp.status_code, 200)
        # 서버가 반환한 HTML 스니펫에 수정된 텍스트가 포함되어 있는지 확인
        self.assertIn('hello', resp.json().get('html', ''))

        # 3) 삭제
        url_d = reverse('board:comment_delete', args=[cid])
        resp = self.client.post(url_d)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(post.comments.count(), 0)
