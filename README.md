# 💰 동아리 회계 관리 시스템

Python 3.8-3.9 + MySQL + Streamlit 기반의 동아리 회계 관리 시스템입니다.

## 🎯 주요 기능

- **거래 입력**: 수입/지출 내역 입력 및 관리
- **중복 방지**: 동일한 거래의 중복 입력 차단
- **지출 경고**: 월별 지출 한도(200,000원) 초과 시 경고
- **모바일 지원**: 반응형 웹 인터페이스
- **월간 대시보드**: 수입/지출 추이 차트 및 통계
- **거래 목록**: 필터링 및 검색 기능

## 🛠️ 기술 스택

- **Backend**: Python 3.8-3.9
- **Database**: MySQL 8.0+
- **Web Framework**: Streamlit 1.22.0
- **Database Driver**: PyMySQL 1.0.2
- **Data Processing**: Pandas 1.5.3
- **Visualization**: Matplotlib 3.7.1

## 📋 설치 및 설정

### 1. Python 환경 설정

```bash
# Python 3.8 또는 3.9 설치 확인
python --version

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. MySQL 데이터베이스 설정

#### 2.1 MySQL 서버 설정

```bash
# MySQL 설정 파일 편집
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# 다음 설정 추가/수정
[mysqld]
bind-address = 0.0.0.0
port = 3306

# MySQL 서비스 재시작
sudo systemctl restart mysql
```

#### 2.2 방화벽 설정

```bash
# Ubuntu/Debian
sudo ufw allow 3306

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=3306/tcp
sudo firewall-cmd --reload
```

#### 2.3 데이터베이스 및 사용자 생성

```sql
-- MySQL에 root로 접속
mysql -u root -p

-- 데이터베이스 생성
CREATE DATABASE solux_finance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 사용자 생성 (보안을 위해 % 대신 특정 IP 사용 권장)
CREATE USER 'solux'@'%' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON solux_finance.* TO 'solux'@'%';
FLUSH PRIVILEGES;

-- 테이블 생성
USE club_finance;
SOURCE database_setup.sql;
```

#### 2.4 보안 권장사항

```sql
-- 특정 IP만 허용하는 경우 (더 안전)
CREATE USER 'solux'@'192.168.1.100' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON solux_finance.* TO 'solux'@'192.168.1.100';

-- 또는 특정 IP 범위 허용
CREATE USER 'solux'@'192.168.1.%' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON solux_finance.* TO 'solux'@'192.168.1.%';
```

### 3. Streamlit 설정

#### 3.1 secrets.toml 파일 설정

`.streamlit/secrets.toml` 파일을 편집하여 실제 데이터베이스 정보를 입력하세요:

```toml
[mysql]
db_host = "your_public_ip_or_domain"  # 실제 공인 IP 또는 도메인
db_port = 3306
db_user = "club_user"
db_password = "your_secure_password"
db_name = "club_finance"
```

#### 3.2 공인 IP 확인

```bash
# Linux/Mac
curl ifconfig.me

# 또는
wget -qO- ifconfig.me
```

## 🚀 실행 방법

### 로컬 실행

```bash
# 프로젝트 디렉토리로 이동
cd solux_finance

# Streamlit 앱 실행
streamlit run app.py
```

### 외부 접속 설정

1. **공인 IP 확인**: `curl ifconfig.me`로 서버의 공인 IP 확인
2. **포트 포워딩**: 라우터에서 8501 포트를 서버로 포워딩
3. **방화벽 설정**: 서버 방화벽에서 8501 포트 개방

```bash
# Ubuntu/Debian
sudo ufw allow 8501

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload
```

4. **외부 접속**: `http://공인IP:8501`로 접속

## ☁️ Streamlit Cloud 배포

### 1. GitHub 저장소 업로드

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/solux_finance.git
git push -u origin main
```

### 2. Streamlit Cloud 설정

1. [Streamlit Cloud](https://share.streamlit.io/)에 로그인
2. "New app" 클릭
3. GitHub 저장소 선택
4. 메인 파일 경로: `app.py`
5. Python 버전: 3.8 또는 3.9 선택

### 3. 환경 변수 설정

Streamlit Cloud 대시보드에서 다음 환경 변수 설정:

```
MYSQL_DB_HOST = your_database_host
MYSQL_DB_PORT = 3306
MYSQL_DB_USER = solux
MYSQL_DB_PASSWORD = your_secure_password
MYSQL_DB_NAME = solux_finance
```

## 📊 데이터베이스 구조

### transactions 테이블
- `id`: 고유 식별자
- `transaction_date`: 거래 날짜
- `transaction_type`: 거래 유형 (수입/지출)
- `amount`: 금액
- `category`: 카테고리
- `description`: 설명
- `created_at`: 생성 시간
- `updated_at`: 수정 시간

### categories 테이블
- `id`: 고유 식별자
- `name`: 카테고리명
- `type`: 카테고리 유형 (수입/지출)

## 🔧 문제 해결

### 데이터베이스 연결 오류

1. **호스트 확인**: `ping your_database_host`
2. **포트 확인**: `telnet your_database_host 3306`
3. **사용자 권한 확인**: MySQL에서 사용자 권한 재설정

### Streamlit 실행 오류

1. **Python 버전 확인**: `python --version`
2. **의존성 재설치**: `pip install -r requirements.txt --force-reinstall`
3. **포트 충돌 확인**: `lsof -i :8501`

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

버그 리포트나 기능 제안은 GitHub Issues를 통해 제출해주세요.
