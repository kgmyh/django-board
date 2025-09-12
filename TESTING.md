테스트 실행 가이드

개요
- Django 내장 테스트 러너를 사용하며, 임시 테스트 데이터베이스에서 실행됩니다.
- board, account 앱의 함수 기반 뷰(FBV) 흐름과 댓글 AJAX 엔드포인트를 검증합니다.

사전 준비
- Python 3.10 이상 권장
- 가상환경(venv) 사용 권장

설치 및 환경 구성
1) 가상환경 생성 및 활성화
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
   - Windows(PowerShell): `python -m venv .venv; .venv\\Scripts\\Activate.ps1`

2) 의존성 설치
   - `pip install -r requirements.txt`
   - 참고: ImageField 사용을 위해 Pillow가 필요하며, 이미 requirements.txt에 포함되어 있습니다.

3) 환경변수 설정(선택)
   - 로컬 개발용 `.env` 파일이 루트에 있습니다. 필요 시 값을 수정하세요.
   - 기본적으로 테스트는 SQLite를 사용하므로 MySQL이 필요하지 않습니다.

4) 개발 DB 마이그레이션(선택)
   - 수동 점검용으로 유용합니다: `python manage.py migrate`

테스트 실행
- 전체 테스트 실행
  - `python manage.py test`

- 로그 상세 출력(verbosity 증가)
  - `python manage.py test -v 2`

- 특정 앱만 실행
  - `python manage.py test board`
  - `python manage.py test account`

- 특정 테스트 케이스/메서드만 실행
  - 케이스: `python manage.py test board.tests.BoardFBVTests`
  - 메서드: `python manage.py test board.tests.BoardFBVTests.test_create_update_delete_flow`

참고 사항
- Django 테스트 클라이언트(`self.client`)는 서버를 띄우지 않고 HTTP 요청을 시뮬레이션합니다.
- 각 테스트 러닝 시 임시 DB가 생성/삭제되어, 테스트 간 상태가 격리됩니다.
- CSRF: 테스트에서는 POST 전용 엔드포인트를 POST로 호출합니다(별도의 토큰 설정 불필요).

문제 해결
- ImportError: 가상환경이 활성화되어 있는지, 의존성이 설치되어 있는지 확인합니다.
- Pillow 관련 에러(ImageField): `pip install --force-reinstall pillow`로 재설치합니다.
- 데이터베이스 에러: 테스트 시 `DB_ENGINE`이 `mysql`로 설정되어 있지 않은지 확인하세요(기본은 SQLite).

커버리지 측정(coverage)
- 설치
  - 글로벌 또는 가상환경에 설치: `pip install coverage`

- 실행(간단)
  - `coverage run --source='account,board' manage.py test`
  - `coverage report -m`  # 터미널 리포트(누락 라인 표시)
  - `coverage html`       # HTML 리포트 생성 → `htmlcov/index.html` 열기

- .coveragerc 사용(권장)
  - 루트의 `.coveragerc`가 포함되어 있습니다. 마이그레이션/설정/관리 스크립트 등은 커버리지 대상에서 제외합니다.
  - 이후에는 더 짧게 실행할 수 있습니다.
    - `coverage run manage.py test`
    - `coverage report -m`

테스트 작성 팁
- 패턴: AAA(Arrange-Act-Assert)
  - Arrange: 테스트에 필요한 데이터/상태 준비
  - Act: 실제 동작(요청/함수 호출) 수행
  - Assert: 기대 결과 검증(상태 코드, 리다이렉트, DB 상태 등)

- 네이밍/구조
  - 테스트 함수 이름은 “검증 대상+시나리오+기대 결과” 형태가 이해에 좋습니다.
  - 파일/클래스/메서드 단위로 주석과 도큐스트링을 적극 활용하세요.

- URL 생성
  - 하드코딩 대신 `reverse('app:view')` 사용 → URL 변경에도 테스트 안정성↑

- 로그인/권한
  - `self.client.login(...)` 또는 `self.client.force_login(user)` 활용
  - 권한 실패 케이스도 함께 테스트(302 to login, 403 등)

- 공통 데이터 준비 성능
  - 여러 테스트에서 재사용하는 고정 데이터는 `setUpTestData`에 생성하면 매 테스트마다 DB insert 비용을 줄일 수 있습니다.
  - 각 테스트에서 변경될 수 있는 객체는 `setUp`에서 생성(테스트 간 상태 격리)

- 응답 검증
  - `assertEqual(resp.status_code, 200)`
  - `assertRedirects(resp, reverse('home'))` 리다이렉트 대상 확인
  - `assertContains(resp, '문자열')` 텍스트 포함 여부
  - JSON: `resp.json()`으로 파싱하고 키/값 검증

- 템플릿/컨텍스트 검증
  - `assertTemplateUsed(resp, 'board/post_list.html')`
  - `self.assertIn('page_obj', resp.context)`

- 쿼리/성능 관련
  - 특정 코드 경로에서 쿼리 수 검증: `with self.assertNumQueries(n): ...`

- 부정(에러) 케이스도 꼭
  - 폼 유효성 실패(필수 값 누락), 권한 실패, 존재하지 않는 리소스(404) 등

- AJAX/Fetch 테스트
  - 본 프로젝트처럼 JSON을 반환하는 엔드포인트는 `self.client.post(url, data)` 후 `resp.json()`으로 검증
  - 필요 시 헤더로 `HTTP_X_REQUESTED_WITH='XMLHttpRequest'`를 추가해 “AJAX 요청”을 흉내낼 수 있습니다.

- 시간/외부 의존성
  - 고정 시간이 필요하면 `unittest.mock`으로 `timezone.now()`를 패치하거나 의존성 주입 패턴 고려
