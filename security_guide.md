# 🔒 보안 강화 가이드

## ⚠️ 현재 보안 위험 요소

1. **MySQL 외부 접속 허용** - 모든 IP에서 접속 가능
2. **간단한 비밀번호** - 추측하기 쉬움
3. **포트 포워딩** - 외부에서 직접 접근 가능
4. **기본 보안 설정 부족**

## 🛡️ 보안 강화 방법

### 1. 특정 IP만 허용 (권장)

#### 1.1 팀원 IP 확인
각 팀원의 고정 IP를 확인하여 특정 IP만 허용:

```sql
-- MySQL에서 특정 IP만 허용하는 사용자 생성
CREATE USER 'solux'@'팀원1_IP' IDENTIFIED BY '강력한_비밀번호';
CREATE USER 'solux'@'팀원2_IP' IDENTIFIED BY '강력한_비밀번호';
CREATE USER 'solux'@'팀원3_IP' IDENTIFIED BY '강력한_비밀번호';

-- 권한 부여
GRANT ALL PRIVILEGES ON solux_finance.* TO 'solux'@'팀원1_IP';
GRANT ALL PRIVILEGES ON solux_finance.* TO 'solux'@'팀원2_IP';
GRANT ALL PRIVILEGES ON solux_finance.* TO 'solux'@'팀원3_IP';

-- 기존 % 사용자 삭제
DROP USER 'solux'@'%';
FLUSH PRIVILEGES;
```

#### 1.2 팀원 IP 확인 방법
각 팀원이 다음 사이트에서 IP 확인:
- https://whatismyipaddress.com/
- https://www.whatismyip.com/

### 2. 강력한 비밀번호 설정

```sql
-- 강력한 비밀번호로 변경 (최소 12자, 특수문자 포함)
ALTER USER 'solux'@'localhost' IDENTIFIED BY 'Solux2024!@#';
ALTER USER 'solux'@'팀원IP' IDENTIFIED BY 'Solux2024!@#';
FLUSH PRIVILEGES;
```

### 3. VPN 사용 (가장 안전)

#### 3.1 VPN 서버 설정
- **OpenVPN** 또는 **WireGuard** 설정
- 팀원들이 VPN을 통해 접속
- 외부 포트 포워딩 불필요

#### 3.2 VPN 사용 시 설정
```sql
-- VPN 내부 IP만 허용
CREATE USER 'solux'@'10.8.0.%' IDENTIFIED BY '강력한_비밀번호';
GRANT ALL PRIVILEGES ON solux_finance.* TO 'solux'@'10.8.0.%';
FLUSH PRIVILEGES;
```

### 4. SSH 터널링 사용

#### 4.1 팀원 설정
```bash
# 팀원들이 SSH 터널 생성 후 접속
ssh -L 3306:localhost:3306 사용자명@123.212.212.221

# 로컬에서 MySQL 접속
mysql -h 127.0.0.1 -u solux -p solux_finance
```

### 5. 방화벽 강화

#### 5.1 Mac 방화벽 활성화
```bash
# 방화벽 활성화
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on

# MySQL만 허용
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/mysql/bin/mysqld
```

#### 5.2 특정 IP만 허용
```bash
# 특정 IP에서만 3306 포트 허용
sudo ufw allow from 팀원1_IP to any port 3306
sudo ufw allow from 팀원2_IP to any port 3306
```

### 6. 접속 로그 모니터링

```sql
-- MySQL 접속 로그 활성화
SET GLOBAL general_log = 'ON';
SET GLOBAL general_log_file = '/usr/local/mysql/data/general.log';

-- 접속 로그 확인
SELECT * FROM mysql.general_log WHERE command_type = 'Connect';
```

### 7. 정기적인 보안 점검

#### 7.1 월 1회 점검 항목
- [ ] 비밀번호 변경
- [ ] 접속 로그 확인
- [ ] 불필요한 사용자 삭제
- [ ] 권한 재검토

#### 7.2 보안 스크립트
```bash
#!/bin/bash
# security_check.sh

echo "=== 보안 점검 시작 ==="

# MySQL 프로세스 확인
ps aux | grep mysql

# 포트 리스닝 확인
lsof -i :3306

# 접속 로그 확인
tail -20 /usr/local/mysql/data/general.log

echo "=== 보안 점검 완료 ==="
```

## 🚨 긴급 보안 조치

### 즉시 실행할 수 있는 조치

1. **강력한 비밀번호로 변경**
```sql
ALTER USER 'solux'@'%' IDENTIFIED BY 'Solux2024!@#Secure';
FLUSH PRIVILEGES;
```

2. **불필요한 사용자 삭제**
```sql
-- 사용자 목록 확인
SELECT User, Host FROM mysql.user;

-- 불필요한 사용자 삭제
DROP USER '불필요한_사용자'@'%';
```

3. **권한 최소화**
```sql
-- 필요한 권한만 부여
REVOKE ALL PRIVILEGES ON *.* FROM 'solux'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON solux_finance.* TO 'solux'@'%';
FLUSH PRIVILEGES;
```

## 📊 보안 수준별 비교

| 방법 | 보안 수준 | 설정 난이도 | 팀원 사용 편의성 |
|------|-----------|-------------|------------------|
| 모든 IP 허용 | ⭐ | 쉬움 | 매우 쉬움 |
| 특정 IP만 허용 | ⭐⭐⭐ | 보통 | 쉬움 |
| VPN 사용 | ⭐⭐⭐⭐⭐ | 어려움 | 보통 |
| SSH 터널링 | ⭐⭐⭐⭐ | 보통 | 어려움 |

## 💡 권장 설정

### 초기 설정 (빠른 보안)
1. 강력한 비밀번호 설정
2. 특정 IP만 허용
3. 접속 로그 활성화

### 장기 설정 (완전한 보안)
1. VPN 서버 구축
2. 정기적인 보안 점검
3. 백업 및 복구 계획

## 🆘 문제 발생 시

### 의심스러운 접속 발견 시
1. **즉시 MySQL 중지**
```bash
sudo /usr/local/mysql/support-files/mysql.server stop
```

2. **로그 확인**
```bash
tail -100 /usr/local/mysql/data/general.log
```

3. **사용자 재설정**
```sql
-- 모든 외부 사용자 삭제 후 재생성
DROP USER 'solux'@'%';
CREATE USER 'solux'@'특정IP' IDENTIFIED BY '새로운_강력한_비밀번호';
```

## 📞 보안 지원

보안 문제 발생 시:
1. 접속 로그 백업
2. 오류 메시지 기록
3. 네트워크 관리자에게 문의
