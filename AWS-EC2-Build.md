**개요**
- AWS EC2(Ubuntu 22.04 기준)에 Docker + Nginx + Gunicorn으로 본 Django 앱을 배포하는 절차입니다.
- 저장소에는 docker-compose, Nginx 설정, Gunicorn 설정, entrypoint 스크립트가 준비되어 있습니다.

**사전 준비**
- 보안그룹: 인바운드 22(SSH), 80(HTTP). 443(HTTPS) 사용 시 추가.
- 키페어: SSH 접속용 키 생성 및 보관.
- 선택: RDS(MySQL) 사용 시, EC2 → RDS 접근 허용(보안그룹/서브넷)과 DB 접속 정보 준비.

**1. EC2 인스턴스 생성**
- AMI: Ubuntu Server 22.04 LTS (권장)
- 인스턴스 타입: t3.small 이상 권장(메모리 여유), 테스트용은 t3.micro 가능
- 스토리지: 최소 20GB 권장(로그/이미지/캐시 고려)
- 네트워크: 퍼블릭 서브넷 + 퍼블릭 IP 할당
- 보안그룹: 22, 80(필수), 443(선택)

**2. 서버 초기 설정**
- SSH 접속: `ssh -i <pem> ubuntu@<EC2_PUBLIC_IP>`
- 패키지 업데이트: `sudo apt-get update && sudo apt-get -y upgrade`
- 시간대 설정(선택): `sudo timedatectl set-timezone Asia/Seoul`

**3. Docker 및 도구 설치**
- Docker Engine 설치
  - `curl -fsSL https://get.docker.com | sudo sh`
  - `sudo usermod -aG docker $USER && newgrp docker` (로그아웃/로그인 필요할 수 있음)
- Docker Compose 플러그인 설치
  - `sudo apt-get install -y docker-compose-plugin`
- Git 설치: `sudo apt-get install -y git`

**4. 애플리케이션 코드 배포**
- 디렉토리 준비: `mkdir -p ~/apps && cd ~/apps`
- 저장소 클론: `git clone https://github.com/kgmyh/django-board.git && cd django-board`
- 브랜치 선택: `git checkout main`

**5. 환경 변수(.env) 설정**
- `.env` 파일 작성(프로젝트 루트)
  - 필수:
    - `DJANGO_SECRET_KEY=<안전한 랜덤 문자열>`
    - `DJANGO_DEBUG=False`
    - `DJANGO_ALLOWED_HOSTS=<도메인 또는 EC2 IP>` (쉼표 구분 다중 가능)
  - DB 선택:
    - SQLite: `DB_ENGINE=sqlite` (기본값)
    - MySQL(RDS):
      - `DB_ENGINE=mysql`
      - `MYSQL_DB=<db명>`
      - `MYSQL_USER=<사용자>`
      - `MYSQL_PASSWORD=<비밀번호>`
      - `MYSQL_HOST=<RDS 엔드포인트>`
      - `MYSQL_PORT=3306`

예시(.env):
```
DJANGO_SECRET_KEY=생성한_랜덤_시크릿
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=example.com,127.0.0.1
DB_ENGINE=sqlite
# MySQL 사용 시 주석 해제
# DB_ENGINE=mysql
# MYSQL_DB=django_board
# MYSQL_USER=appuser
# MYSQL_PASSWORD=StrongPassword!
# MYSQL_HOST=mydb.cluster-xxxx.ap-northeast-2.rds.amazonaws.com
# MYSQL_PORT=3306
```

**6. Docker Compose 실행**
- 빌드 및 기동: `docker compose up -d --build`
  - web(앱) 컨테이너가 migrate, collectstatic 후 Gunicorn으로 기동됩니다.
  - nginx 컨테이너가 80 포트로 서비스합니다.
- 상태 확인: `docker compose ps`
- 로그 확인:
  - 앱: `docker compose logs -f web`
  - Nginx: `docker compose logs -f nginx`

**7. 접속/확인**
- 브라우저에서 `http://<EC2_PUBLIC_IP>/` 접속
- 관리자 계정 생성(최초 1회): `docker compose exec web python manage.py createsuperuser`

**8. 도메인 연결(선택)**
- 도메인 A레코드 → EC2 퍼블릭 IP 지정
- `.env`의 `DJANGO_ALLOWED_HOSTS`에 도메인 추가
- 적용 후 재기동: `docker compose up -d`

**9. HTTPS 구성(선택)**
- 간단 옵션: 상위 레이어(Load Balancer/CloudFront)에서 TLS 종료 후 HTTP로 프록시
- Nginx 컨테이너에 인증서 적용(커스텀 conf + cert/key 마운트)
  - Certbot를 호스트에서 운영하거나, 별도 컨테이너로 운영 가능
  - Nginx 서버블록에 `listen 443 ssl;` 및 인증서 경로 설정 필요

**10. 운영 팁**
- 부팅 시 자동 시작: `sudo systemctl enable docker`
- 재배포
  - 코드 갱신: `git pull`
  - 재빌드/재시작: `docker compose up -d --build`
  - 마이그레이션/정적 수집: entrypoint에서 자동 수행
- 로그 로테이션: CloudWatch/CloudWatch Agent 또는 외부 로깅 연계 고려
- 모니터링/알람: EC2/ALB의 헬스체크, CloudWatch 경보 설정 권장

**문제 해결**
- 502 Bad Gateway(Nginx)
  - web 컨테이너 기동 여부 확인: `docker compose ps`
  - web 로그에서 Gunicorn 에러 확인: `docker compose logs -f web`
  - `.env`의 ALLOWED_HOSTS, DB 설정 오류 점검
- 정적 파일 미표시
  - web 컨테이너에서 `collectstatic` 성공 여부 확인(엔트리포인트 자동 실행)
  - nginx 컨테이너에 static/media 볼륨 마운트 상태 확인
- DB 연결 실패
  - RDS 보안그룹과 네트워크 설정 확인, MYSQL_* 값 재검토

