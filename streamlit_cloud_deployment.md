# Streamlit Cloud 배포 가이드

## 🚀 배포 개요

Streamlit Cloud를 사용하여 동아리 회계 관리 시스템을 무료로 배포할 수 있습니다.

### 장점
- 무료 호스팅
- 자동 HTTPS
- GitHub 연동
- 자동 배포

### 제한사항
- 데이터베이스는 외부 MySQL 서버 필요
- 무료 플랜: 앱당 1GB RAM, 1GB 디스크
- 동시 사용자 제한

## 📋 사전 준비

### 1. GitHub 저장소 준비

```bash
# 로컬 저장소 초기화
git init
git add .
git commit -m "Initial commit: 동아리 회계 관리 시스템"

# GitHub 저장소 생성 후 연결
git remote add origin https://github.com/yourusername/solux_finance.git
git branch -M main
git push -u origin main
```

### 2. 외부 MySQL 서버 준비

Streamlit Cloud는 데이터베이스를 제공하지 않으므로 외부 MySQL 서버가 필요합니다.

#### 옵션 1: 자체 서버
- VPS 또는 클라우드 서버
- MySQL 8.0+ 설치
- 외부 접속 설정

#### 옵션 2: 클라우드 데이터베이스
- **AWS RDS**: MySQL 호스팅
- **Google Cloud SQL**: MySQL 호스팅
- **Azure Database for MySQL**: MySQL 호스팅
- **PlanetScale**: MySQL 호스팅 (무료 티어 있음)

#### 옵션 3: 무료 MySQL 호스팅
- **Clever Cloud**: 무료 MySQL 데이터베이스
- **Railway**: 무료 티어로 MySQL 제공
- **Render**: 무료 PostgreSQL (MySQL 대신 사용 가능)

## 🔧 Streamlit Cloud 배포

### 1단계: Streamlit Cloud 가입

1. [Streamlit Cloud](https://share.streamlit.io/) 접속
2. GitHub 계정으로 로그인
3. GitHub 권한 승인

### 2단계: 새 앱 생성

1. **"New app"** 버튼 클릭
2. **Repository**: `yourusername/solux_finance` 선택
3. **Branch**: `main` 선택
4. **Main file path**: `app.py` 입력
5. **Python version**: `3.8` 또는 `3.9` 선택

### 3단계: 환경 변수 설정

Streamlit Cloud 대시보드에서 **"Settings"** → **"Secrets"** 탭으로 이동하여 다음 내용 입력:

```toml
[mysql]
db_host = "your-mysql-server.com"
db_port = 3306
db_user = "solux"
db_password = "your_secure_password"
db_name = "solux_finance"
```

### 4단계: 배포 확인

1. **"Deploy"** 버튼 클릭
2. 배포 로그 확인
3. 앱 URL 확인 (예: `https://your-app-name.streamlit.app`)

## 🔒 보안 설정

### 1. 데이터베이스 보안

```sql
-- 특정 IP만 허용 (Streamlit Cloud IP)
-- Streamlit Cloud IP 확인 후 설정
CREATE USER 'solux'@'35.196.xxx.xxx' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON solux_finance.* TO 'solux'@'35.196.xxx.xxx';
FLUSH PRIVILEGES;
```

### 2. SSL 연결 강제

```sql
-- SSL 연결 강제
ALTER USER 'solux'@'%' REQUIRE SSL;
FLUSH PRIVILEGES;
```

### 3. 방화벽 설정

```bash
# MySQL 서버에서 Streamlit Cloud IP만 허용
sudo ufw allow from 35.196.0.0/16 to any port 3306
```

## 🔧 문제 해결

### 1. 배포 실패

#### 로그 확인
```bash
# Streamlit Cloud 대시보드에서 로그 확인
# 일반적인 오류:
# - 데이터베이스 연결 실패
# - 패키지 설치 실패
# - Python 버전 호환성 문제
```

#### 해결 방법
1. **데이터베이스 연결 확인**
   ```python
   # test_connection.py
   import pymysql
   
   try:
       connection = pymysql.connect(
           host='your-mysql-server.com',
           port=3306,
                   user='solux',
        password='your_password',
           database='solux_finance'
       )
       print("연결 성공!")
       connection.close()
   except Exception as e:
       print(f"연결 실패: {e}")
   ```

2. **패키지 버전 확인**
   ```txt
   # requirements.txt 수정
   streamlit==1.22.0
   pymysql==1.0.2
   pandas==1.5.3
   matplotlib==3.7.1
   numpy==1.24.3
   ```

### 2. 데이터베이스 연결 오류

#### 일반적인 원인
- 방화벽 차단
- 잘못된 호스트/IP
- 사용자 권한 문제
- SSL 설정 문제

#### 해결 방법
```bash
# MySQL 서버에서 연결 테스트
mysql -h localhost -u solux -p solux_finance

# 포트 리스닝 확인
sudo netstat -tlnp | grep 3306

# 방화벽 상태 확인
sudo ufw status
```

### 3. 성능 문제

#### 메모리 사용량 최적화
```python
# app.py에서 메모리 최적화
import gc

def cleanup_memory():
    """메모리 정리"""
    gc.collect()

# 대용량 데이터 처리 후 호출
cleanup_memory()
```

#### 데이터베이스 연결 풀링
```python
# 연결 풀 사용 (선택사항)
import pymysql
from dbutils.pooled_db import PooledDB

# 연결 풀 생성
pool = PooledDB(
    creator=pymysql,
    maxconnections=6,
    mincached=2,
    maxcached=5,
    maxshared=3,
    blocking=True,
    maxusage=None,
    setsession=[],
    ping=0,
    host=st.secrets["mysql"]["db_host"],
    port=st.secrets["mysql"]["db_port"],
    user=st.secrets["mysql"]["db_user"],
    password=st.secrets["mysql"]["db_password"],
    database=st.secrets["mysql"]["db_name"],
    charset='utf8mb4'
)

def get_connection():
    """연결 풀에서 연결 가져오기"""
    return pool.connection()
```

## 📊 모니터링 및 관리

### 1. 앱 성능 모니터링

Streamlit Cloud 대시보드에서 확인 가능:
- 앱 상태
- 배포 로그
- 사용량 통계
- 오류 로그

### 2. 데이터베이스 모니터링

```sql
-- 연결 상태 확인
SHOW PROCESSLIST;

-- 쿼리 성능 확인
SHOW STATUS LIKE 'Slow_queries';

-- 테이블 크기 확인
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'club_finance';
```

### 3. 백업 설정

```bash
#!/bin/bash
# backup_script.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="club_finance_${DATE}.sql"

# 데이터베이스 백업
mysqldump -h your-mysql-server.com -u club_user -p club_finance > $BACKUP_FILE

# 압축
gzip $BACKUP_FILE

# 클라우드 스토리지 업로드 (선택사항)
# aws s3 cp ${BACKUP_FILE}.gz s3://your-backup-bucket/
```

## 🔄 업데이트 및 유지보수

### 1. 코드 업데이트

```bash
# 로컬에서 코드 수정
git add .
git commit -m "Update: 새로운 기능 추가"
git push origin main

# Streamlit Cloud에서 자동 배포됨
```

### 2. 데이터베이스 마이그레이션

```sql
-- 새로운 테이블 추가
CREATE TABLE IF NOT EXISTS new_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100)
);

-- 기존 데이터 마이그레이션
INSERT INTO new_table (name) 
SELECT DISTINCT category FROM transactions;
```

### 3. 환경 변수 업데이트

Streamlit Cloud 대시보드에서:
1. **Settings** → **Secrets**
2. 환경 변수 수정
3. **Save** 클릭
4. 앱 재배포

## 📱 모바일 최적화

### 1. 반응형 디자인 확인

```python
# app.py에서 모바일 최적화
st.set_page_config(
    page_title="동아리 회계 관리",
    page_icon="💰",
    layout="wide",  # 모바일에서도 적절히 표시
    initial_sidebar_state="collapsed"  # 모바일에서 사이드바 접기
)
```

### 2. 터치 친화적 UI

```python
# 큰 버튼과 터치 영역
if st.button("저장", type="primary", use_container_width=True):
    # 저장 로직

# 간단한 폼
with st.form("simple_form"):
    st.text_input("설명", key="description")
    st.form_submit_button("제출", use_container_width=True)
```

## 🆘 지원 및 문의

### Streamlit Cloud 지원
- [Streamlit Cloud 문서](https://docs.streamlit.io/streamlit-community-cloud)
- [GitHub Issues](https://github.com/streamlit/streamlit/issues)

### 문제 해결 체크리스트
- [ ] GitHub 저장소가 공개되어 있는가?
- [ ] requirements.txt가 올바른가?
- [ ] 데이터베이스 연결 정보가 정확한가?
- [ ] MySQL 서버가 외부 접속을 허용하는가?
- [ ] 방화벽이 3306 포트를 허용하는가?

### 로그 분석
```bash
# Streamlit Cloud 로그에서 확인할 키워드
# ERROR: 오류 메시지
# WARNING: 경고 메시지
# Connection refused: 데이터베이스 연결 실패
# ModuleNotFoundError: 패키지 설치 실패
```
