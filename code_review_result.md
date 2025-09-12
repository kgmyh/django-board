 요약

  - 전반적으로 기본 구조는 깔끔합니다만, 보안 설정 노출, 작성자 저장 버그, 권한/HTTP 메서드 처리, 정적/미디어
  자산 관리 등이 시급합니다.
  - Django 버전(요구사항 5.1)과 코드 베이스(3.2 시절 패턴) 불일치로 인한 잠재 오류가 있습니다.
  - 중복 정적 파일 및 collectstatic 산출물 커밋 등 불필요/위험 요소가 있습니다.

  치명·우선 수정

  - Secret/DB 설정 노출: config/settings.py에 SECRET_KEY, DB 호스트/유저/비밀번호가 하드코딩되어 있습니다.
      - 환경변수(.env + python-dotenv 혹은 django-environ)로 분리하고, Git에 커밋 금지.
      - DEBUG는 기본 False, 개발/운영 분리 설정(settings/local.py vs settings/production.py) 권장.
  - 작성자 저장 버그: PostCreateView.form_valid()에서 post = form.save(commit=False)로 객체 만들고 post.writer
  를 셋팅하지만 super().form_valid(form) 호출로 덮여 저장되어 writer가 반영되지 않습니다.
      - 수정: form.instance.writer = get_user(self.request); return super().form_valid(form)
  - 삭제 처리의 HTTP/권한 문제:
      - 현재 GET으로 삭제 수행 및 단순 로그인만 확인 → CSRF/의도치 않은 요청/권한 문제.
      - 수정: @login_required + POST 전용 + 작성자 본인 또는 권한자만 삭제. 예: UserPassesTestMixin 또는 함수
  기반에서 if request.user != post.writer: return HttpResponseForbidden().
  - Pagination 버그:
      - previous_page_number, next_page_number는 메서드 호출 필요함. 현재 템플릿 컨텍스트에서 함수 객체가 전달
  됩니다.
      - 게시글 0건일 때 page_range 인덱싱(page_range[0]) 예외 발생 가능 → 빈 케이스 가드 필요.

  보안/설정

  - urlpatterns += static(...): 개발용(디버그)에서만 미디어 서빙하도록 if settings.DEBUG: 조건으로 감싸기.
  - ALLOWED_HOSTS: 운영/개발분리, 로컬 개발 시 localhost, 127.0.0.1 포함.
  - Django 5.1 호환성:
      - USE_L10N는 Django 5에서 제거됨 → 설정에서 삭제.
      - 전체 코드 Django 5에서 실행 확인 필요.
  - 관리자 정적파일 커밋 금지: static/admin/...은 collectstatic 산출물로 보이며, 저장소에서 제거 + .gitignore
  유지.

  중복/정리 포인트

  - 정적 파일 중복:
      - static/board/tiger.jpg와 board/static/board/tiger.jpg가 중복. 앱 정적 경로(board/static/...)만 사용하
  고 home.html의 경로도 {% static 'board/tiger.jpg' %}로 통일.
      - static/lion.jpg, static_files/lion.jpg, static/lionking.jpg 등도 정리: STATICFILES_DIRS는 외부 공용 자
  산만, 앱 전용은 각 앱의 static로 이동.
  - STATIC_ROOT=static은 안티패턴: 배포용 수집 디렉토리와 개발용 정적 디렉토리를 분리. 예: STATIC_ROOT =
  BASE_DIR / 'static_collected'.
  - templates/home.html의 static 태그 사용:
      - "{% static '/board/tiger.jpg' %}"처럼 슬래시로 시작하면 잘못된 URL이 생성될 수 있음 → 선행 슬래시
  제거.

  코드 품질/모듈화

  - 권한 믹스인 활용:
      - PostUpdateView/삭제에 LoginRequiredMixin, UserPassesTestMixin 또는 커스텀 OwnerRequiredMixin 적용해 로
  직 공통화.
  - 쿼리 최적화:
      - Detail/List 접근 시 select_related('writer', 'category')로 조인 최적화. 특히 상세 템플릿에서 category
  접근하므로 DetailView get_queryset()에서 붙이는 것이 안전.
  - 예외/404 처리:
      - 삭제에서 Post.objects.get(pk=pk) → get_object_or_404(Post, pk=pk).
  - Null 안전 출력:
      - post_detail.html에서 object.category.category_name은 NPE 위험 → {{ object.category.category_name|
  default:'-' }} 또는 {% if object.category %}...{% endif %}.
  - URL 정책:
      - 경로에 슬래시(/create/, /list/ 등) 붙이기 + APPEND_SLASH 기본 정책 일관화. 현재 일부 경로는 확장자/슬
  래시 불일치.
  - Admin 커스터마이징:
      - UserAdmin.fieldsets[1][1]['fields']를 직접 변경하지 말고 class CustomUserAdmin(UserAdmin): fieldsets =
  UserAdmin.fieldsets + ((...),)처럼 서브클래스에서 정의. 전역 UserAdmin 변경 부작용 가능.
  - import/불필요 코드:
      - account/views.py의 render 미사용.
      - board/urls.py의 미사용 TemplateView import 제거.
  - 템플릿 마크업:
      - templates/layout.html에서 <li class='nav-item'></li> 하나가 열고 닫힌 뒤 외부에 <a> 태그가 있습니다.
  <li> 내부에 <a>가 들어가도록 수정 필요.

  테스트/운영

  - 테스트 없음: 최소한의 기능 테스트 추가 권장
      - 가입/로그인, 게시글 생성(writer 저장 확인), 수정/삭제 권한, 목록 페이징(0건/경계/다음그룹) 테스트.
  - 배포 설정 파일:
      - config/uwsgi/mysite.ini에 절대경로/사용자명 하드코딩 → 운영 환경변수/템플릿화 권장.
  - requirements와 실제 코드 정합성:
      - Django 5.1 명시되어 있으니 마이그레이션, 설정 및 코드 전체 Django 5 기준 점검 필요.

  권장 변경 예시 스니펫

  - Post 작성자 저장 버그 수정:
      - board/views.py in PostCreateView.form_valid:
      - form.instance.writer = get_user(self.request)
      - return super().form_valid(form)
  - 삭제 권한/POST 전용:
      - URL에 path('delete/<int:pk>/', views.post_delete, name='delete')
      - view에서 if request.method != 'POST': return HttpResponseNotAllowed(['POST']), 권한 체크 추가, 템플릿
  은 <form method="post">+CSRF로 변경.
  - 페이지네이션 컨텍스트:
      - 메서드 호출 수정: start_page.previous_page_number() / end_page.next_page_number()
      - 0건 가드: if paginator.num_pages == 0: context.update({...}) 빠른 반환.

  정리 체크리스트

  - 환경변수로 설정 분리(.env) 및 시크릿 제거
  - STATIC_ROOT 분리, admin/static 수집물 제거, 정적 파일 중복 정리
  - PostCreateView 작성자 저장/권한/HTTP 메서드 보강
  - 페이지네이션 메서드 호출/엣지 케이스 처리
  - Django 5 호환성(설정 및 제거된 항목) 정리
  - 템플릿 마크업/정적 경로 수정
  - Admin 커스터마이징 안전화
  - select_related로 조회 최적화
  - 기본 테스트 추가