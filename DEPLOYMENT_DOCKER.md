Docker 배포 (Nginx + Gunicorn)

구성 개요
- Gunicorn: Django WSGI 앱 실행
- Nginx: 리버스 프록시 + 정적/미디어 파일 서빙
- docker-compose: web(앱) + nginx 컨테이너 오케스트레이션

디렉토리/파일
- docker/app/Dockerfile: 앱 컨테이너 빌드 설정
- docker/app/entrypoint.sh: migrate/collectstatic 후 gunicorn 실행
- docker/nginx/default.conf: Nginx 설정 (정적/미디어/프록시)
- docker-compose.yml: 서비스 정의(web, nginx)
- gunicorn.conf.py: Gunicorn 설정(환경변수로 튜닝 가능)
- .dockerignore: 도커 컨텍스트 제외 목록

사전 준비
- .env에 필요한 설정 등록 (예시는 루트에 이미 존재)
  - 기본은 SQLite 사용(DB_ENGINE=sqlite). MySQL 사용 시 DB_ENGINE=mysql 및 MYSQL_* 값 설정
  - DJANGO_DEBUG=False, DJANGO_ALLOWED_HOSTS=* 또는 실제 도메인 지정 권장

빌드 및 실행
1) 빌드 및 시작
   - `docker-compose up -d --build`

2) 로그 확인
   - 앱: `docker-compose logs -f web`
   - Nginx: `docker-compose logs -f nginx`

3) 접속
   - http://localhost/ (호스트 80 포트 매핑)

정적/미디어 파일
- web 컨테이너에서 collectstatic → /app/static (STATIC_ROOT)
- nginx 컨테이너는 static_volume를 /static, media_volume를 /media로 마운트하여 직접 서빙

마이그레이션/슈퍼유저
- entrypoint.sh가 자동으로 `python manage.py migrate` 실행
- 슈퍼유저 생성은 1회 수동 실행
  - `docker-compose exec web python manage.py createsuperuser`

Gunicorn 튜닝(환경변수)
- GUNICORN_WORKERS, GUNICORN_THREADS, GUNICORN_TIMEOUT 등으로 조정
  - 예) `GUNICORN_WORKERS=4 GUNICORN_THREADS=2`

운영 팁
- DJANGO_ALLOWED_HOSTS에 실제 도메인/프록시 호스트 기입
- HTTPS 종단은 상위 레이어(로드밸런서/리버스 프록시)에서 처리하거나, Nginx에 인증서 적용
- MySQL 사용 시 데이터베이스 연결 확인 및 healthcheck/wait-for-db 스크립트 도입 고려

