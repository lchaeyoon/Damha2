import streamlit as st
import pandas as pd
import io
from datetime import datetime

def process_blog_titles(df):
    """블로그 제목 데이터 처리"""
    try:
        # 새로운 데이터프레임 생성
        result_df = pd.DataFrame()
        
        # 필요한 열만 선택하고 처리
        result_df['제목'] = df['제목'].str.strip()
        result_df['URL'] = df['URL'].str.strip()
        result_df['작성일'] = pd.to_datetime(df['작성일']).dt.strftime('%Y-%m-%d')
        result_df['블로그명'] = df['블로그명'].str.strip()
        result_df['닉네임'] = df['닉네임'].str.strip()
        
        return result_df
    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {str(e)}")
        return None

def main():
    st.title("블로그 제목 추출 시스템")
    
    # 사이드바에 설명 추가
    with st.sidebar:
        st.markdown("""
        ### 사용 방법
        1. 엑셀 파일 업로드
        2. 데이터 미리보기 확인
        3. '제목 추출 시작' 버튼 클릭
        4. 결과 파일 다운로드
        
        ### 필수 열
        - 제목
        - URL
        - 작성일
        - 블로그명
        - 닉네임
        """)
    
    # 파일 업로드
    uploaded_file = st.file_uploader(
        "블로그 데이터 엑셀 파일을 선택하세요 (.xlsx)", 
        type=['xlsx']
    )
    
    if uploaded_file:
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(uploaded_file)
            
            # 필수 열 확인
            required_columns = ['제목', 'URL', '작성일', '블로그명', '닉네임']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"다음 열이 없습니다: {', '.join(missing_columns)}")
                return
            
            # 데이터 미리보기
            st.write("### 원본 데이터 미리보기:")
            st.write(df.head())
            
            if st.button("제목 추출 시작"):
                with st.spinner("데이터 처리 중..."):
                    # 진행 상황 표시
                    progress_bar = st.progress(0)
                    
                    # 데이터 처리
                    result_df = process_blog_titles(df)
                    
                    if result_df is not None:
                        # 결과 미리보기
                        st.write("### 처리 결과 미리보기:")
                        st.write(result_df.head())
                        
                        # 엑셀 파일로 변환
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            result_df.to_excel(writer, index=False, sheet_name='블로그제목')
                        
                        # 현재 날짜로 파일명 생성
                        current_date = datetime.now().strftime('%Y%m%d')
                        
                        # 결과 파일 다운로드
                        st.download_button(
                            label="📥 추출 결과 다운로드",
                            data=buffer.getvalue(),
                            file_name=f"블로그제목추출_{current_date}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                        st.success("✅ 제목 추출이 완료되었습니다!")
                        
                        # 통계 정보 표시
                        st.write("### 📊 데이터 통계")
                        st.write(f"- 총 게시글 수: {len(result_df):,}개")
                        st.write(f"- 고유 블로그 수: {result_df['블로그명'].nunique():,}개")
                
        except Exception as e:
            st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main() 
