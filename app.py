"""
solux 회계 관리 시스템
Python 3.8-3.9 + MySQL + Streamlit
"""

import streamlit as st
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
import calendar
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="solux 회계 관리",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_connection():
    """데이터베이스 연결 함수"""
    try:
        connection = pymysql.connect(
            host=st.secrets["mysql"]["db_host"],
            port=st.secrets["mysql"]["db_port"],
            user=st.secrets["mysql"]["db_user"],
            password=st.secrets["mysql"]["db_password"],
            database=st.secrets["mysql"]["db_name"],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        st.error(f"데이터베이스 연결 실패: {str(e)}")
        return None

def check_duplicate_transaction(transaction_date, transaction_type, amount, category, description):
    """중복 거래 확인"""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT COUNT(*) as count FROM transactions 
            WHERE transaction_date = %s 
            AND transaction_type = %s 
            AND amount = %s 
            AND category = %s 
            AND description = %s
            """
            cursor.execute(sql, (transaction_date, transaction_type, amount, category, description))
            result = cursor.fetchone()
            return result['count'] > 0
    except Exception as e:
        st.error(f"중복 확인 중 오류: {str(e)}")
        return False
    finally:
        connection.close()

def check_monthly_expense_limit(transaction_date, amount):
    """월별 지출 한도 확인 (200,000원)"""
    connection = get_connection()
    if not connection:
        return False, 0
    
    try:
        with connection.cursor() as cursor:
            # 해당 월의 총 지출 계산
            year_month = transaction_date.strftime('%Y-%m')
            sql = """
            SELECT COALESCE(SUM(amount), 0) as total_expense 
            FROM transactions 
            WHERE transaction_type = '지출' 
            AND DATE_FORMAT(transaction_date, '%%Y-%%m') = %s
            """
            cursor.execute(sql, (year_month,))
            result = cursor.fetchone()
            current_total = result['total_expense']
            
            # 새로운 거래 추가 시 총액
            new_total = current_total + amount
            return new_total > 200000, new_total
    except Exception as e:
        st.error(f"월별 지출 확인 중 오류: {str(e)}")
        return False, 0
    finally:
        connection.close()

def insert_transaction(transaction_date, transaction_type, amount, category, description):
    """거래 내역 저장"""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO transactions (transaction_date, transaction_type, amount, category, description)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (transaction_date, transaction_type, amount, category, description))
            connection.commit()
            return True
    except Exception as e:
        st.error(f"거래 저장 중 오류: {str(e)}")
        return False
    finally:
        connection.close()

def get_transactions(limit=100):
    """거래 내역 조회"""
    connection = get_connection()
    if not connection:
        return pd.DataFrame()
    
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT * FROM transactions 
            ORDER BY transaction_date DESC, created_at DESC 
            LIMIT %s
            """
            cursor.execute(sql, (limit,))
            results = cursor.fetchall()
            return pd.DataFrame(results)
    except Exception as e:
        st.error(f"거래 내역 조회 중 오류: {str(e)}")
        return pd.DataFrame()
    finally:
        connection.close()

def get_categories(transaction_type=None):
    """카테고리 목록 조회"""
    connection = get_connection()
    if not connection:
        return []
    
    try:
        with connection.cursor() as cursor:
            if transaction_type:
                sql = "SELECT name FROM categories WHERE type = %s ORDER BY name"
                cursor.execute(sql, (transaction_type,))
            else:
                sql = "SELECT name FROM categories ORDER BY type, name"
                cursor.execute(sql)
            
            results = cursor.fetchall()
            return [row['name'] for row in results]
    except Exception as e:
        st.error(f"카테고리 조회 중 오류: {str(e)}")
        return []
    finally:
        connection.close()

def get_monthly_data(year_month):
    """월별 데이터 조회"""
    connection = get_connection()
    if not connection:
        return pd.DataFrame()
    
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT 
                transaction_date,
                transaction_type,
                SUM(amount) as daily_total
            FROM transactions 
            WHERE DATE_FORMAT(transaction_date, '%%Y-%%m') = %s
            GROUP BY transaction_date, transaction_type
            ORDER BY transaction_date
            """
            cursor.execute(sql, (year_month,))
            results = cursor.fetchall()
            return pd.DataFrame(results)
    except Exception as e:
        st.error(f"월별 데이터 조회 중 오류: {str(e)}")
        return pd.DataFrame()
    finally:
        connection.close()

# 메인 애플리케이션
def main():
    st.title("💰 동아리 회계 관리 시스템")
    st.markdown("---")
    
    # 사이드바 메뉴
    menu = st.sidebar.selectbox(
        "메뉴 선택",
        ["🏠 대시보드", "📝 거래 입력", "📊 거래 목록", "📈 월별 통계"]
    )
    
    if menu == "🏠 대시보드":
        show_dashboard()
    elif menu == "📝 거래 입력":
        show_transaction_form()
    elif menu == "📊 거래 목록":
        show_transaction_list()
    elif menu == "📈 월별 통계":
        show_monthly_statistics()

def show_dashboard():
    """대시보드 화면"""
    st.header("🏠 대시보드")
    
    # 현재 월 데이터 조회
    current_month = datetime.now().strftime('%Y-%m')
    monthly_data = get_monthly_data(current_month)
    
    if not monthly_data.empty:
        # 수입/지출 합계 계산
        income_total = monthly_data[monthly_data['transaction_type'] == '수입']['daily_total'].sum()
        expense_total = monthly_data[monthly_data['transaction_type'] == '지출']['daily_total'].sum()
        balance = income_total - expense_total
        
        # 메트릭 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("이번 달 수입", f"{income_total:,.0f}원")
        
        with col2:
            st.metric("이번 달 지출", f"{expense_total:,.0f}원")
        
        with col3:
            st.metric("잔액", f"{balance:,.0f}원", delta=f"{balance:,.0f}원")
        
        with col4:
            # 지출 한도 경고
            if expense_total > 200000:
                st.error("⚠️ 지출 한도 초과!")
            else:
                remaining = 200000 - expense_total
                st.info(f"지출 한도: {remaining:,.0f}원 남음")
        
        # 월별 차트
        st.subheader("이번 달 수입/지출 추이")
        
        if not monthly_data.empty:
            # 차트 데이터 준비
            chart_data = monthly_data.pivot_table(
                index='transaction_date', 
                columns='transaction_type', 
                values='daily_total', 
                aggfunc='sum'
            ).fillna(0)
            
            # matplotlib 차트 생성
            fig, ax = plt.subplots(figsize=(12, 6))
            
            if '수입' in chart_data.columns:
                ax.plot(chart_data.index, chart_data['수입'], marker='o', linewidth=2, label='수입', color='green')
            
            if '지출' in chart_data.columns:
                ax.plot(chart_data.index, chart_data['지출'], marker='s', linewidth=2, label='지출', color='red')
            
            ax.set_xlabel('날짜')
            ax.set_ylabel('금액 (원)')
            ax.set_title(f'{current_month} 수입/지출 추이')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # x축 날짜 포맷팅
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            st.pyplot(fig)
    else:
        st.info("이번 달 거래 내역이 없습니다.")

def show_transaction_form():
    """거래 입력 폼"""
    st.header("📝 거래 입력")
    
    with st.form("transaction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_date = st.date_input("거래 날짜", value=date.today())
            transaction_type = st.selectbox("거래 유형", ["수입", "지출"])
            amount = st.number_input("금액 (원)", min_value=0, step=1000, value=0)
        
        with col2:
            # 카테고리 동적 로딩
            categories = get_categories(transaction_type)
            category = st.selectbox("카테고리", categories)
            description = st.text_area("설명", height=100)
        
        submitted = st.form_submit_button("저장")
        
        if submitted:
            if amount <= 0:
                st.error("금액은 0보다 커야 합니다.")
                return
            
            if not description.strip():
                st.error("설명을 입력해주세요.")
                return
            
            # 중복 확인
            if check_duplicate_transaction(transaction_date, transaction_type, amount, category, description):
                st.error("⚠️ 동일한 거래가 이미 존재합니다. (날짜, 유형, 금액, 카테고리, 설명이 모두 동일)")
                return
            
            # 지출 한도 확인
            if transaction_type == "지출":
                over_limit, total_expense = check_monthly_expense_limit(transaction_date, amount)
                if over_limit:
                    st.warning(f"⚠️ 월별 지출 한도(200,000원)를 초과합니다! 총 지출: {total_expense:,.0f}원")
                    if not st.checkbox("경고를 무시하고 저장하시겠습니까?"):
                        return
            
            # 거래 저장
            if insert_transaction(transaction_date, transaction_type, amount, category, description):
                st.success("✅ 거래가 성공적으로 저장되었습니다!")
                st.balloons()
            else:
                st.error("❌ 거래 저장에 실패했습니다.")

def show_transaction_list():
    """거래 목록 조회"""
    st.header("📊 거래 목록")
    
    # 필터 옵션
    col1, col2, col3 = st.columns(3)
    
    with col1:
        transaction_type_filter = st.selectbox("거래 유형", ["전체", "수입", "지출"])
    
    with col2:
        limit = st.selectbox("표시 개수", [50, 100, 200, 500])
    
    with col3:
        if st.button("새로고침"):
            st.experimental_rerun()
    
    # 거래 내역 조회
    transactions_df = get_transactions(limit)
    
    if not transactions_df.empty:
        # 필터 적용
        if transaction_type_filter != "전체":
            transactions_df = transactions_df[transactions_df['transaction_type'] == transaction_type_filter]
        
        # 날짜 포맷팅
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date']).dt.strftime('%Y-%m-%d')
        transactions_df['amount'] = transactions_df['amount'].apply(lambda x: f"{x:,.0f}원")
        
        # 표시할 컬럼만 선택
        display_df = transactions_df[['transaction_date', 'transaction_type', 'amount', 'category', 'description']]
        display_df.columns = ['날짜', '유형', '금액', '카테고리', '설명']
        
        st.dataframe(display_df, use_container_width=True)
        
        # 통계 정보
        st.subheader("📈 통계 정보")
        total_income = transactions_df[transactions_df['transaction_type'] == '수입']['amount'].str.replace('원', '').str.replace(',', '').astype(float).sum()
        total_expense = transactions_df[transactions_df['transaction_type'] == '지출']['amount'].str.replace('원', '').str.replace(',', '').astype(float).sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 수입", f"{total_income:,.0f}원")
        with col2:
            st.metric("총 지출", f"{total_expense:,.0f}원")
        with col3:
            st.metric("순액", f"{total_income - total_expense:,.0f}원")
    else:
        st.info("거래 내역이 없습니다.")

def show_monthly_statistics():
    """월별 통계"""
    st.header("📈 월별 통계")
    
    # 월 선택
    current_year = datetime.now().year
    selected_year = st.selectbox("연도", range(current_year-2, current_year+1), index=2)
    selected_month = st.selectbox("월", range(1, 13), index=datetime.now().month-1)
    
    year_month = f"{selected_year:04d}-{selected_month:02d}"
    
    # 월별 데이터 조회
    monthly_data = get_monthly_data(year_month)
    
    if not monthly_data.empty:
        # 수입/지출 합계
        income_total = monthly_data[monthly_data['transaction_type'] == '수입']['daily_total'].sum()
        expense_total = monthly_data[monthly_data['transaction_type'] == '지출']['daily_total'].sum()
        
        # 메트릭
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("월 수입", f"{income_total:,.0f}원")
        with col2:
            st.metric("월 지출", f"{expense_total:,.0f}원")
        with col3:
            st.metric("월 잔액", f"{income_total - expense_total:,.0f}원")
        
        # 차트
        st.subheader(f"{year_month} 수입/지출 추이")
        
        # 차트 데이터 준비
        chart_data = monthly_data.pivot_table(
            index='transaction_date', 
            columns='transaction_type', 
            values='daily_total', 
            aggfunc='sum'
        ).fillna(0)
        
        # matplotlib 차트
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if '수입' in chart_data.columns:
            ax.plot(chart_data.index, chart_data['수입'], marker='o', linewidth=2, label='수입', color='green')
        
        if '지출' in chart_data.columns:
            ax.plot(chart_data.index, chart_data['지출'], marker='s', linewidth=2, label='지출', color='red')
        
        ax.set_xlabel('날짜')
        ax.set_ylabel('금액 (원)')
        ax.set_title(f'{year_month} 수입/지출 추이')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(fig)
        
        # 카테고리별 분석
        st.subheader("카테고리별 분석")
        
        # 카테고리별 데이터 조회
        connection = get_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = """
                    SELECT category, transaction_type, SUM(amount) as total
                    FROM transactions 
                    WHERE DATE_FORMAT(transaction_date, '%%Y-%%m') = %s
                    GROUP BY category, transaction_type
                    ORDER BY transaction_type, total DESC
                    """
                    cursor.execute(sql, (year_month,))
                    category_data = cursor.fetchall()
                    
                    if category_data:
                        category_df = pd.DataFrame(category_data)
                        
                        # 수입/지출별로 분리
                        income_categories = category_df[category_df['transaction_type'] == '수입']
                        expense_categories = category_df[category_df['transaction_type'] == '지출']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if not income_categories.empty:
                                st.write("**수입 카테고리**")
                                for _, row in income_categories.iterrows():
                                    st.write(f"- {row['category']}: {row['total']:,.0f}원")
                        
                        with col2:
                            if not expense_categories.empty:
                                st.write("**지출 카테고리**")
                                for _, row in expense_categories.iterrows():
                                    st.write(f"- {row['category']}: {row['total']:,.0f}원")
            except Exception as e:
                st.error(f"카테고리 분석 중 오류: {str(e)}")
            finally:
                connection.close()
    else:
        st.info(f"{year_month} 거래 내역이 없습니다.")

if __name__ == "__main__":
    main()
