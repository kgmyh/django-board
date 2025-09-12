"""
self.client는 Django의 테스트 클라이언트로, 테스트 코드에서 실제 웹 브라우저처럼 HTTP 요청(GET, POST 등)을 시뮬레이션할 수 있게 해주는 도구입니다.
이를 통해 뷰 함수가 실제 요청을 받았을 때와 동일하게 동작하는지 테스트할 수 있습니다.

주요 기능:

GET, POST, PUT, DELETE 등 HTTP 요청을 테스트 환경에서 보낼 수 있습니다.
로그인/로그아웃 등 세션 기반 인증을 시뮬레이션할 수 있습니다.
응답 객체(resp)를 통해 상태 코드, 본문, 리다이렉트 등 결과를 검증할 수 있습니다.
즉, 실제 사용자가 웹사이트를 이용하는 것처럼 테스트를 자동화할 수 있게 해줍니다.
"""

"""
board/tests.py

이 파일은 게시판(Board) 앱의 함수 기반 뷰(FBV)가 정상 동작하는지 확인하는 단위 테스트를 담고 있습니다.

핵심 포인트 요약
- Django TestCase는 매 테스트를 트랜잭션으로 감싸고, 별도의 테스트 데이터베이스를 사용합니다.
- self.client는 Django의 테스트 클라이언트로, HTTP 요청(get/post 등)을 시뮬레이션합니다.
- reverse('app_name:view_name')는 URL 하드코딩을 피하고, urlpattern의 name으로 주소를 역으로 생성합니다.
- assertEqual/Contains 등 단언(assert) 메서드로 응답 상태 코드나 내용, DB 상태를 검증합니다.
"""

from django.test import TestCase  # Django의 테스트 베이스 클래스를 임포트
from django.urls import reverse  # urlpattern name으로 URL을 생성하기 위해 사용
from django.contrib.auth import get_user_model  # 설정된 사용자 모델을 얻기 위해 사용
from .models import Post, Category  # 테스트 대상 모델
from django.test import RequestFactory  # 뷰를 직접 호출하여 순수 쿼리 수를 측정할 때 사용
from .views import post_detail, post_list  # FBV를 직접 호출하기 위해 임포트


class BoardFBVTests(TestCase):  # 게시판 관련 FBV 테스트 모음
    """게시판 FBV들의 기본 플로우를 검증하는 테스트 모음입니다."""

    def setUp(self):
        """
        매 테스트 실행 전에 기본 사용자와 카테고리를 하나씩 생성합니다.
        - setUp은 각 테스트 케이스(method)마다 새로 수행되며, 테스트 간 상태가 공유되지 않습니다.
        """
        # 테스트용 사용자 생성 (비밀번호는 해시되어 저장)
        self.user = get_user_model().objects.create_user(
            username='tester', password='pass1234', name='Tester', email='t@e.st', gender='M'
        )
        # 기본 카테고리 생성
        self.category = Category.objects.create(category_name='일반')

    def test_list_view(self):
        """
        글 목록 페이지가 정상적으로 200 OK를 반환하는지 확인합니다.
        - 로그인은 필요하지 않은 공개 페이지이므로, 인증 없이 접근합니다.
        """
        # urls.py에서 board:list url을 가져온다.
        url = reverse('board:list')  # URL name으로 목록 주소 생성
        # http get 요청을 한다. 
        resp = self.client.get(url)  # GET 요청 전송
        # 응답 status 가 200이면 OK
        self.assertEqual(resp.status_code, 200)  # 200 OK 기대

    def test_create_requires_login(self):
        """
        글 작성 페이지는 로그인한 사용자만 접근할 수 있습니다.
        - 비로그인 상태에서 접근 시 로그인 페이지로 302 리다이렉트되는지 확인합니다.
        """
        url = reverse('board:create')  # 글 작성 URL 생성
        resp = self.client.get(url)  # 비로그인 상태로 접근
        self.assertEqual(resp.status_code, 302)  # 로그인 페이지로 리다이렉트 기대

    def test_create_update_delete_flow(self):
        """
        글 생성→상세조회→수정→삭제의 전체 플로우를 검증합니다.
        - client.login(...) 으로 세션 기반 로그인을 시뮬레이션합니다.
        - 생성/수정 요청은 POST로 보내며, 성공 시 302 리다이렉트가 기대됩니다.
        - 삭제는 현재 동작상 GET으로 처리하므로 GET 요청 후 목록으로 302 리다이렉트를 기대합니다.
        """
        # 1) 로그인
        self.client.login(username='tester', password='pass1234')  # 세션 로그인 시뮬레이션

        # 2) 생성 (POST)
        create_url = reverse('board:create')  # 생성 엔드포인트
        data = {
            'title': '제목',  # 제목 필드
            'content': '내용',  # 내용 필드
            'category': self.category.pk,  # 외래키: 카테고리 PK 제출
        }
        resp = self.client.post(create_url, data)  # POST로 생성 요청
        self.assertEqual(resp.status_code, 302)  # 성공 시 리다이렉트
        post = Post.objects.first()  # 첫 번째(유일한) 게시글 조회
        self.assertIsNotNone(post)  # 생성되었는지 확인

        # 3) 상세 조회 (GET)
        detail_url = reverse('board:detail', args=[post.pk])  # 상세 주소 생성
        resp = self.client.get(detail_url)  # 상세 GET 요청
        self.assertContains(resp, '제목')  # 응답 본문에 텍스트 포함 여부 확인

        # 4) 수정 (POST)
        update_url = reverse('board:update', args=[post.pk])  # 수정 주소 생성
        resp = self.client.post(update_url, {**data, 'title': '제목2'})  # 제목만 변경해 POST
        self.assertEqual(resp.status_code, 302)  # 성공 리다이렉트
        post.refresh_from_db()  # DB에서 다시 읽어 변경 반영 확인
        self.assertEqual(post.title, '제목2')  # 제목 변경 검증

        # 5) 삭제 (GET)
        delete_url = reverse('board:delete', args=[post.pk])  # 삭제 URL 생성
        resp = self.client.get(delete_url)  # 현재 구현은 GET 삭제
        self.assertEqual(resp.status_code, 302)  # 성공 리다이렉트
        self.assertEqual(Post.objects.count(), 0)  # 게시글 수 0 확인

    def test_comments_crud(self):
        """
        댓글의 생성/수정/삭제 AJAX 엔드포인트를 검증합니다.
        - 댓글 API는 로그인 필요 + POST 전용입니다.
        - 응답은 JSON이며, 성공 시 ok=True와 일부 HTML 스니펫을 반환합니다.
        """
        self.client.login(username='tester', password='pass1234')  # 로그인

        # 테스트용 게시글 생성 (댓글을 달 대상)
        post = Post.objects.create(title='t', content='c', category=self.category, writer=self.user)

        # 1) 생성
        url = reverse('board:comment_create', args=[post.pk])  # 생성 엔드포인트
        resp = self.client.post(url, {'content': 'hi'})  # 내용만 제출
        self.assertEqual(resp.status_code, 200)  # JSON 200 OK
        cid = post.comments.first().pk  # 생성된 댓글 PK

        # 2) 수정
        url_u = reverse('board:comment_update', args=[cid])  # 수정 주소
        resp = self.client.post(url_u, {'content': 'hello'})  # 수정 POST
        self.assertEqual(resp.status_code, 200)  # JSON 200 OK
        # 서버가 반환한 HTML 스니펫에 수정된 텍스트가 포함되어 있는지 확인
        self.assertIn('hello', resp.json().get('html', ''))

        # 3) 삭제
        url_d = reverse('board:comment_delete', args=[cid])  # 삭제 주소
        resp = self.client.post(url_d)  # 삭제 POST
        self.assertEqual(resp.status_code, 200)  # JSON 200 OK
        self.assertEqual(post.comments.count(), 0)  # 댓글 수 0 확인

    def test_post_detail_query_count_constant_with_many_comments(self):
        """
        assertNumQueries로 상세보기의 쿼리 수를 검증합니다.

        핵심 아이디어
        - 상세 뷰는 다음과 같은 DB 접근을 수행합니다.
          1) 게시글 1건 조회 (get_object_or_404) → 1 쿼리
          2) 댓글 목록 조회 (select_related('writer')로 작성자 조인) → 1 쿼리
          3) 템플릿에서 게시글의 카테고리 접근(object.category.category_name) → 1 쿼리
          4) 템플릿에서 작성자 비교(object.writer.pk)로 접근 → 1 쿼리
          합계: 4 쿼리 (댓글 개수와 무관하게 select_related로 N+1 방지)

        - RequestFactory를 사용하면 미들웨어/세션으로 인한 부수 쿼리 없이
          뷰 호출/템플릿 렌더링 범위에서 발생한 쿼리만 측정할 수 있습니다.
        """
        # Arrange: 데이터 준비 (게시글 + 많은 댓글)
        self.client.login(username='tester', password='pass1234')
        post = Post.objects.create(title='T', content='C', category=self.category, writer=self.user)
        # 댓글 20개 생성 (select_related 덕분에 조회 쿼리는 1회로 유지되어야 함)
        for i in range(20):
            post.comments.create(writer=self.user, content=f'C{i}')

        rf = RequestFactory()
        request = rf.get(f'/board/detail/{post.pk}')
        request.user = self.user  # 템플릿 내 작성자 비교 분기 유발

        # Act + Assert: 쿼리 수가 4회로 고정되는지 검증
        with self.assertNumQueries(4):
            resp = post_detail(request, post.pk)
            self.assertEqual(resp.status_code, 200)

    def test_post_list_query_count_with_pagination(self):
        """
        목록 뷰의 쿼리 수를 검증합니다.

        개념 정리
        - Django의 Paginator는 전체 개수를 구하기 위한 COUNT 쿼리 1회,
          특정 페이지 데이터를 가져오는 SELECT 쿼리 1회를 수행하는 것이 일반적입니다.
        - 템플릿에서 외래키 접근 등을 하지 않으므로 기본적으로 2회 쿼리를 기대합니다.
        """
        # Arrange: 여러 게시글 생성 (페이지네이션 동작 확인용)
        Post.objects.bulk_create([
            Post(title=f'T{i}', content='C', category=self.category, writer=self.user)
            for i in range(25)
        ])

        rf = RequestFactory()
        request = rf.get('/board/list?page=1')

        # Act + Assert: COUNT 1회 + 페이지 데이터 1회 = 총 2회로 검증
        with self.assertNumQueries(2):
            resp = post_list(request)
            self.assertEqual(resp.status_code, 200)
