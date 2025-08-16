# MySQL 외부 접속 설정 가이드

## 🔒 보안 고려사항

⚠️ **중요**: 외부 접속을 허용하기 전에 다음 보안 사항을 반드시 확인하세요.

### 1. 강력한 비밀번호 사용
- 최소 12자 이상
- 대소문자, 숫자, 특수문자 포함
- 예측 가능한 패턴 사용 금지

### 2. 특정 IP만 허용 (권장)
- `%` 대신 특정 IP 주소 사용
- 팀원들의 고정 IP 주소 확인
- VPN 사용 고려

## 📋 단계별 설정

### 1단계: MySQL 서버 설정

#### Ubuntu/Debian
```bash
# MySQL 설정 파일 편집
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# 다음 설정 추가/수정
[mysqld]
bind-address = 0.0.0.0
port = 3306
max_connections = 100
```

#### CentOS/RHEL
```bash
# MySQL 설정 파일 편집
sudo nano /etc/my.cnf

# 다음 설정 추가/수정
[mysqld]
bind-address = 0.0.0.0
port = 3306
max_connections = 100
```

#### Windows
```ini
# my.ini 파일 편집
[mysqld]
bind-address = 0.0.0.0
port = 3306
max_connections = 100
```

### 2단계: MySQL 서비스 재시작

```bash
# Ubuntu/Debian
sudo systemctl restart mysql

# CentOS/RHEL
sudo systemctl restart mysqld

# Windows
net stop mysql
net start mysql
```

### 3단계: 방화벽 설정

#### Ubuntu/Debian (ufw)
```bash
# MySQL 포트 허용
sudo ufw allow 3306/tcp

# 방화벽 상태 확인
sudo ufw status
```

#### CentOS/RHEL (firewalld)
```bash
# MySQL 포트 허용
sudo firewall-cmd --permanent --add-port=3306/tcp
sudo firewall-cmd --reload

# 방화벽 상태 확인
sudo firewall-cmd --list-ports
```

#### Windows (Windows Defender)
1. 제어판 → 시스템 및 보안 → Windows Defender 방화벽
2. 고급 설정 → 인바운드 규칙 → 새 규칙
3. 포트 선택 → TCP → 특정 포트: 3306
4. 연결 허용 → 도메인, 개인, 공용 모두 선택
5. 이름: "MySQL Database"

### 4단계: 데이터베이스 및 사용자 생성

```sql
-- MySQL에 root로 접속
mysql -u root -p

-- 데이터베이스 생성
CREATE DATABASE solux_finance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 보안 사용자 생성 (권장 방법)
-- 방법 1: 특정 IP만 허용
CREATE USER 'solux'@'192.168.1.100' IDENTIFIED BY 'MySecurePassword123!';
GRANT ALL PRIVILEGES ON solux_finance.* TO 'solux'@'192.168.1.100';

-- 방법 2: IP 범위 허용
CREATE USER 'solux'@'192.168.1.%' IDENTIFIED BY 'MySecurePassword123!';
GRANT ALL PRIVILEGES ON solux_finance.* TO 'solux'@'192.168.1.%';

-- 방법 3: 모든 IP 허용 (보안상 권장하지 않음)
CREATE USER 'solux'@'%' IDENTIFIED BY 'MySecurePassword123!';
GRANT ALL PRIVILEGES ON solux_finance.* TO 'solux'@'%';

-- 권한 적용
FLUSH PRIVILEGES;

-- 사용자 확인
SELECT User, Host FROM mysql.user WHERE User = 'solux';

-- 테이블 생성
USE solux_finance;
SOURCE database_setup.sql;
```

### 5단계: 연결 테스트

#### 로컬에서 테스트
```bash
# MySQL 클라이언트로 연결 테스트
mysql -h localhost -u solux -p solux_finance
```

#### 외부에서 테스트
```bash
# 다른 컴퓨터에서 연결 테스트
mysql -h YOUR_SERVER_IP -u solux -p solux_finance
```

#### Python으로 테스트
```python
import pymysql

try:
    connection = pymysql.connect(
        host='YOUR_SERVER_IP',
        port=3306,
        user='solux',
        password='MySecurePassword123!',
        database='solux_finance',
        charset='utf8mb4'
    )
    print("연결 성공!")
    connection.close()
except Exception as e:
    print(f"연결 실패: {e}")
```

## 🔧 문제 해결

### 1. 연결 거부 오류

```bash
# MySQL 상태 확인
sudo systemctl status mysql

# 포트 리스닝 확인
sudo netstat -tlnp | grep 3306

# MySQL 로그 확인
sudo tail -f /var/log/mysql/error.log
```

### 2. 권한 오류

```sql
-- 사용자 권한 확인
SHOW GRANTS FOR 'solux'@'%';

-- 권한 재설정
REVOKE ALL PRIVILEGES ON solux_finance.* FROM 'solux'@'%';
GRANT ALL PRIVILEGES ON solux_finance.* TO 'solux'@'%';
FLUSH PRIVILEGES;
```

### 3. 방화벽 문제

```bash
# 포트 스캔으로 확인
nmap -p 3306 YOUR_SERVER_IP

# telnet으로 연결 테스트
telnet YOUR_SERVER_IP 3306
```

## 🛡️ 보안 강화 방법

### 1. SSH 터널링 사용 (권장)

```bash
# SSH 터널 생성
ssh -L 3306:localhost:3306 user@YOUR_SERVER_IP

# 로컬에서 연결
mysql -h 127.0.0.1 -u club_user -p club_finance
```

### 2. VPN 사용

- OpenVPN 또는 WireGuard 설정
- VPN을 통해서만 데이터베이스 접속 허용

### 3. SSL/TLS 연결

```sql
-- SSL 인증서 생성 후
ALTER USER 'club_user'@'%' REQUIRE SSL;
FLUSH PRIVILEGES;
```

### 4. 접속 로그 모니터링

```sql
-- 로그 활성화
SET GLOBAL general_log = 'ON';
SET GLOBAL general_log_file = '/var/log/mysql/general.log';

-- 접속 로그 확인
SELECT * FROM mysql.general_log WHERE command_type = 'Connect';
```

## 📱 모바일 접속 설정

### 1. 공인 IP 확인

```bash
# 서버의 공인 IP 확인
curl ifconfig.me
```

### 2. 라우터 포트 포워딩

1. 라우터 관리 페이지 접속
2. 포트 포워딩 설정
3. 외부 포트: 3306 → 내부 IP: 서버IP, 내부 포트: 3306

### 3. 동적 DNS 설정 (권장)

- No-IP, DuckDNS 등 서비스 사용
- 도메인 이름으로 접속 가능

## 🔄 백업 및 복구

### 자동 백업 스크립트

```bash
#!/bin/bash
# backup_mysql.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/mysql"
DB_NAME="solux_finance"

# 백업 디렉토리 생성
mkdir -p $BACKUP_DIR

# 백업 실행
mysqldump -u solux -p solux_finance > $BACKUP_DIR/${DB_NAME}_${DATE}.sql

# 30일 이상 된 백업 삭제
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
```

### crontab 설정

```bash
# crontab 편집
crontab -e

# 매일 새벽 2시에 백업
0 2 * * * /path/to/backup_mysql.sh
```

## 📞 지원

문제가 발생하면 다음 정보를 포함하여 문의하세요:

1. 운영체제 및 버전
2. MySQL 버전
3. 오류 메시지 전체
4. 시도한 해결 방법
5. 네트워크 환경 (공유기, 방화벽 등)
