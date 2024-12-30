import streamlit as st
import pandas as pd
import io
from datetime import datetime

def main():
    st.title("블로그 제목 추출 시스템")
    
    # 파일 업로드
    uploaded_file = st.file_uploader("블로그 데이터 엑셀 파일을 선택하세요", type=['xlsx'])
    
    if uploaded_file:
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(uploaded_file)
            
            # 데이터 미리보기
            st.write("### 데이터 미리보기:")
            st.write(df.head())
            
            if st.button("제목 추출 시작"):
                # 진행 상황 표시
                progress_text = st.empty()
                progress_bar = st.progress(0)
                
                try:
                    # 새로운 데이터프레임 생성
                    result_df = pd.DataFrame()
                    
                    # 필요한 열만 선택
                    result_df['제목'] = df['제목'].str.strip()
                    result_df['URL'] = df['URL'].str.strip()
                    result_df['작성일'] = df['작성일']
                    
                    # 날짜 형식 변환
                    result_df['작성일'] = pd.to_datetime(result_df['작성일']).dt.strftime('%Y-%m-%d')
                    
                    # 결과 미리보기
                    st.write("### 추출 결과 미리보기:")
                    st.write(result_df.head())
                    
                    # 엑셀 파일로 변환
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        result_df.to_excel(writer, index=False, sheet_name='블로그제목')
                    
                    # 현재 날짜로 파일명 생성
                    current_date = datetime.now().strftime('%Y%m%d')
                    
                    # 결과 파일 다운로드
                    st.download_button(
                        label="추출 결과 다운로드",
                        data=buffer.getvalue(),
                        file_name=f"블로그제목추출_{current_date}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    st.success("제목 추출이 완료되었습니다!")
                    
                except Exception as e:
                    st.error(f"제목 추출 중 오류가 발생했습니다: {str(e)}")
                
        except Exception as e:
            st.error(f"파일 읽기 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main() 
