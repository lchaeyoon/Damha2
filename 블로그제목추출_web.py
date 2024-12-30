import streamlit as st
import pandas as pd
import io
from datetime import datetime

def main():
    st.title("블로그 제목 자동 추출 시스템")
    
    with st.sidebar:
        st.markdown("""
        ### 안내사항
        현재 이 웹 앱은 로컬에서만 실행 가능합니다.
        
        로컬 실행 방법:
        1. Python 설치
        2. 필요한 라이브러리 설치:
           ```
           pip install streamlit pandas selenium chromedriver-autoinstaller
           ```
        3. 코드 실행:
           ```
           streamlit run 블로그제목추출.py
           ```
        """)
    
    st.warning("⚠️ 보안 정책상 웹에서는 자동 로그인 기능을 사용할 수 없습니다.")
    st.info("이 기능을 사용하려면 로컬에서 실행해주세요.")
    
    # 수동 입력 옵션 제공
    st.write("### 수동으로 데이터 입력")
    uploaded_file = st.file_uploader("블로그 데이터 엑셀 파일을 선택하세요", type=['xlsx'])
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.write("### 데이터 미리보기")
            st.write(df.head())
            
            if st.button("데이터 처리"):
                # 결과 저장
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                
                # 다운로드 버튼
                current_date = datetime.now().strftime('%Y%m%d')
                st.download_button(
                    label="📥 파일 다운로드",
                    data=buffer.getvalue(),
                    file_name=f"블로그제목_{current_date}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main() 
