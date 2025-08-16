#!/usr/bin/env python3
"""
데이터베이스 연결 테스트 스크립트
Python 3.8-3.9 호환
"""

import pymysql
import sys
import os
import toml

def test_mysql_connection():
    """MySQL 연결 테스트"""
    
    # .streamlit/secrets.toml 파일에서 설정 읽기
    secrets_file = ".streamlit/secrets.toml"
    
    if not os.path.exists(secrets_file):
        print(f"❌ secrets 파일 없음: {secrets_file}")
        return False
    
    try:
        with open(secrets_file, 'r', encoding='utf-8') as f:
            secrets = toml.load(f)
        
        db_config = {
            'host': secrets['db']['host'],
            'port': int(secrets['db']['port']),
            'user': secrets['db']['user'],
            'password': secrets['db']['password'],
            'database': secrets['db']['database'],
            'charset': 'utf8mb4'
        }
    except Exception as e:
        print(f"❌ secrets 파일 읽기 오류: {e}")
        return False
    
    print("🔍 데이터베이스 연결 테스트 시작...")
    print(f"호스트: {db_config['host']}")
    print(f"포트: {db_config['port']}")
    print(f"사용자: {db_config['user']}")
    print(f"데이터베이스: {db_config['database']}")
    print("-" * 50)
    
    try:
        # 연결 시도
        connection = pymysql.connect(**db_config)
        print("✅ 데이터베이스 연결 성공!")
        
        # 테이블 존재 확인
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print(f"📋 발견된 테이블: {len(tables)}개")
            for table in tables:
                print(f"  - {table[0]}")
            
            # transactions 테이블 데이터 확인
            if tables:
                cursor.execute("SELECT COUNT(*) as count FROM transactions")
                result = cursor.fetchone()
                print(f"📊 거래 내역 수: {result[0]}건")
                
                # 최근 거래 3건 조회
                cursor.execute("""
                    SELECT transaction_date, transaction_type, amount, category, description 
                    FROM transactions 
                    ORDER BY created_at DESC 
                    LIMIT 3
                """)
                recent_transactions = cursor.fetchall()
                
                if recent_transactions:
                    print("📈 최근 거래 내역:")
                    for tx in recent_transactions:
                        print(f"  - {tx[0]}: {tx[1]} {tx[2]:,}원 ({tx[3]}) - {tx[4]}")
                else:
                    print("📈 거래 내역이 없습니다.")
        
        connection.close()
        print("✅ 테스트 완료!")
        return True
        
    except pymysql.Error as e:
        print(f"❌ MySQL 오류: {e}")
        return False
    except Exception as e:
        print(f"❌ 일반 오류: {e}")
        return False

def test_streamlit_secrets():
    """Streamlit secrets 파일 테스트"""
    print("\n🔍 Streamlit secrets 파일 테스트...")
    
    secrets_file = ".streamlit/secrets.toml"
    
    if os.path.exists(secrets_file):
        print(f"✅ secrets 파일 발견: {secrets_file}")
        
        try:
            with open(secrets_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print("📄 파일 내용:")
                print(content)
        except Exception as e:
            print(f"❌ 파일 읽기 오류: {e}")
    else:
        print(f"❌ secrets 파일 없음: {secrets_file}")
        print("💡 .streamlit/secrets.toml 파일을 생성하고 데이터베이스 정보를 입력하세요.")

def main():
    """메인 함수"""
    print("🚀 동아리 회계 관리 시스템 - 연결 테스트")
    print("=" * 60)
    
    # Streamlit secrets 테스트
    test_streamlit_secrets()
    
    print("\n" + "=" * 60)
    
    # MySQL 연결 테스트
    success = test_mysql_connection()
    
    print("\n" + "=" * 60)
    
    if success:
        print("🎉 모든 테스트가 성공했습니다!")
        print("💡 이제 'streamlit run app.py' 명령으로 앱을 실행할 수 있습니다.")
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")
        print("💡 다음을 확인하세요:")
        print("  1. MySQL 서버가 실행 중인가?")
        print("  2. 데이터베이스 연결 정보가 올바른가?")
        print("  3. 방화벽이 3306 포트를 허용하는가?")
        print("  4. 사용자 권한이 올바른가?")

if __name__ == "__main__":
    main()
