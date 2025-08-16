-- 동아리 회계 관리 시스템 데이터베이스 설정
-- MySQL 8.0 이상에서 실행

-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS solux_finance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 데이터베이스 사용
USE solux_finance;

-- 거래 내역 테이블
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_date DATE NOT NULL,
    transaction_type ENUM('수입', '지출') NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 중복 입력 방지를 위한 유니크 인덱스
    UNIQUE KEY unique_transaction (
        transaction_date, 
        transaction_type, 
        amount, 
        category, 
        description(100)
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 카테고리 테이블 (기본 카테고리)
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    type ENUM('수입', '지출') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 기본 카테고리 데이터 삽입
INSERT IGNORE INTO categories (name, type) VALUES
-- 수입 카테고리
('회비', '수입'),
('후원금', '수입'),
('기타 수입', '수입'),
-- 지출 카테고리
('식비', '지출'),
('교통비', '지출'),
('재료비', '지출'),
('행사비', '지출'),
('기타 지출', '지출');

-- 샘플 데이터 (테스트용)
INSERT IGNORE INTO transactions (transaction_date, transaction_type, amount, category, description) VALUES
('2023-01-15', '수입', 50000.00, '회비', '송지민 재입금'),
('2023-01-20', '지출', 150000.00, '식비', '회식'),
('2023-01-25', '지출', 8000.00, '교통비', '행사 참여 교통비'),
('2023-02-01', '수입', 30000.00, '후원금', '교수님 지원금'),
('2023-02-10', '지출', 25000.00, '강의비', '깃허브 강의비 구매');
