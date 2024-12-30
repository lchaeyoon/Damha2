import streamlit as st
import re
import feedparser
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build

def extract_blog_titles(credentials_json):
    try:
        # 구글 스프레드시트 정보
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/1ufCsVjPm1YJ6FvipTcKDuvGddVWQqJeF_6sahTpO7nk/edit#gid=1320512368"
        spreadsheet_id = re.search(r"/d/(\S+)/edit", spreadsheet_url).group(1)
        original_sheet_name = '업체관리'
        cell_range = 'C6:F'

        # Google Sheets API 인증 설정
        credentials = service_account.Credentials.from_service_account_info(credentials_json)
        scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/spreadsheets'])
        service = build('sheets', 'v4', credentials=scoped_credentials)

        # 진행 상황 표시
        progress_text = st.empty()
        progress_bar = st.progress(0)

        # URL 리스트 가져오기
        progress_text.text("URL 리스트 가져오는 중...")
        url_range = f'{original_sheet_name}!L6:L'
        url_values = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, 
            range=url_range
        ).execute().get('values', [])

        # 업체명 리스트 가져오기
        progress_text.text("업체명 리스트 가져오는 중...")
        company_names_range = f'{original_sheet_name}!B6:B'
        company_names_values = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, 
            range=company_names_range
        ).execute().get('values', [])

        if url_values and company_names_values:
            total_items = len(url_values)
            
            for index, (url_data, company_name_data) in enumerate(zip(url_values, company_names_values), 1):
                if not url_data or not company_name_data:
                    continue

                url = url_data[0]
                company_name = company_name_data[0]
                
                progress = index / total_items
                progress_bar.progress(progress)
                progress_text.text(f"처리 중... ({index}/{total_items}): {company_name}")

                # 시트 존재 여부 확인
                sheet_names = [sheet['properties']['title'] for sheet in 
                             service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()['sheets']]
                new_sheet_name = company_name

                if new_sheet_name not in sheet_names:
                    # 새로운 시트 생성
                    new_sheet_request = {
                        'requests': [{
                            'duplicateSheet': {
                                'sourceSheetId': service.spreadsheets().get(
                                    spreadsheetId=spreadsheet_id
                                ).execute()['sheets'][0]['properties']['sheetId'],
                                'insertSheetIndex': 1,
                                'newSheetName': new_sheet_name
                            }
                        }]
                    }
                    service.spreadsheets().batchUpdate(
                        spreadsheetId=spreadsheet_id, 
                        body=new_sheet_request
                    ).execute()
                    st.info(f"새로운 시트 '{new_sheet_name}'가 생성되었습니다.")

                # RSS 피드 가져오기
                feed = feedparser.parse(url)

                # RSS 피드에서 정보 추출
                max_items_to_fetch = 50
                items = feed.get("items", [])[:max_items_to_fetch]

                data = []
                for item in items:
                    title = item.get("title", "")
                    author = item.get("author", "")
                    link = item.get("link", "")
                    published = item.get("published", "")
                    data.append([title, author, link, published])

                # 구글 시트에 데이터 입력
                body = {"values": data}
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f'{new_sheet_name}!{cell_range}',
                    body=body,
                    valueInputOption='USER_ENTERED'
                ).execute()
                st.success(f"'{new_sheet_name}' 시트에 데이터가 입력되었습니다.")

            st.success("모든 처리가 완료되었습니다! 🎉")
            
            # 스프레드시트 링크 제공
            st.markdown(f"### [구글 스프레드시트 열기]({spreadsheet_url})")
            
        else:
            st.error("데이터를 찾을 수 없습니다.")

    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")

def main():
    st.title("블로그 제목 자동 추출 시스템")
    
    with st.sidebar:
        st.markdown("""
        ### 사용 방법
        1. 구글 서비스 계정 키 파일(.json) 업로드
        2. '제목 추출 시작' 버튼 클릭
        3. 처리 완료 후 스프레드시트 확인
        """)
    
    # 서비스 계정 키 파일 업로드
    credentials_file = st.file_uploader(
        "구글 서비스 계정 키 파일을 선택하세요 (.json)", 
        type=['json']
    )
    
    if credentials_file:
        credentials_json = credentials_file.getvalue()
        credentials_dict = eval(credentials_json.decode('utf-8'))
        
        if st.button("제목 추출 시작"):
            extract_blog_titles(credentials_dict)

if __name__ == "__main__":
    main() 
