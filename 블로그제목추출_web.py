import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import time
from datetime import datetime
import io

def setup_chrome_driver():
    """크롬 드라이버 설정"""
    try:
        chromedriver_autoinstaller.install()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')  # 백그라운드 실행
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        st.error(f"크롬 드라이버 설정 중 오류: {str(e)}")
        return None

def extract_blog_titles():
    """블로그 제목 추출 실행"""
    try:
        driver = setup_chrome_driver()
        if not driver:
            return None
            
        # 진행 상태 표시
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        # 네이버 로그인 페이지로 이동
        status_text.text("네이버 로그인 페이지로 이동 중...")
        driver.get("https://nid.naver.com/nidlogin.login")
        
        # 로그인 정보 입력 대기
        st.warning("⚠️ 보안을 위해 직접 로그인이 필요합니다")
        st.info("로그인이 완료되면 '다음 단계로' 버튼을 클릭해주세요")
        
        if st.button("다음 단계로"):
            # 블로그 관리 페이지로 이동
            status_text.text("블로그 관리 페이지로 이동 중...")
            driver.get("https://blog.naver.com/BlogAdmin.naver")
            time.sleep(2)
            
            # 데이터 추출
            titles = []
            urls = []
            dates = []
            blog_names = []
            nicknames = []
            
            # 여기에 기존 코드의 데이터 추출 로직 추가
            # ...
            
            # 결과 데이터프레임 생성
            result_df = pd.DataFrame({
                '제목': titles,
                'URL': urls,
                '작성일': dates,
                '블로그명': blog_names,
                '닉네임': nicknames
            })
            
            # 결과 저장
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                result_df.to_excel(writer, index=False)
            
            # 다운로드 버튼
            current_date = datetime.now().strftime('%Y%m%d')
            st.download_button(
                label="📥 추출 결과 다운로드",
                data=buffer.getvalue(),
                file_name=f"블로그제목추출_{current_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.success("✅ 제목 추출이 완료되었습니다!")
            
        driver.quit()
        
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")
        if driver:
            driver.quit()

def main():
    st.title("블로그 제목 자동 추출 시스템")
    
    with st.sidebar:
        st.markdown("""
        ### 사용 방법
        1. '시작하기' 버튼 클릭
        2. 네이버 로그인
        3. '다음 단계로' 버튼 클릭
        4. 추출 완료 후 결과 다운로드
        """)
    
    if st.button("시작하기"):
        extract_blog_titles()

if __name__ == "__main__":
    main() 
