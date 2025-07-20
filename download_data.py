import requests

# --- 사용자 설정 ---
# 아래 변수에 자신의 구글 시트 '내보내기' URL을 입력하세요.
# URL 형식: "https://docs.google.com/spreadsheets/d/{스프레드시트_ID}/export?format=csv&gid={시트_ID}"
# 예시: sheet_url = "https://docs.google.com/spreadsheets/d/1Qyg2AI8aA4z1K_4x_s2y_3z_4w_5v_6u_7x_8y_9z_0/export?format=csv&gid=0"
sheet_url = "https://docs.google.com/spreadsheets/d/1wPVxiGGzLk-u4AdLpkrEZZLB0wb5hZQSqKxqCSdLmRg/export?format=csv&gid=1126038564"

# 저장할 파일 이름
output_filename = "data.csv"


def download_sheet_as_csv(url, filename):
    """
    주어진 URL에서 구글 시트를 다운로드하여 CSV 파일로 저장합니다.
    한글 깨짐과 불필요한 빈 줄 문제를 해결합니다.
    """
    print(f"다운로드 시작: {url}")

    try:
        # URL에 GET 요청을 보내 응답을 받습니다.
        response = requests.get(url)
        
        # 요청이 성공했는지 확인합니다 (HTTP 상태 코드가 200이 아닐 경우 예외 발생).
        response.raise_for_status()
        
        # 응답의 인코딩을 UTF-8로 명시적으로 설정합니다.
        response.encoding = 'utf-8'
        
        # CSV 파일을 'utf-8-sig' 인코딩으로 저장합니다.
        # 'utf-8-sig'는 파일 시작에 BOM(Byte Order Mark)을 추가하여
        # Microsoft Excel과 같은 프로그램이 UTF-8 파일을 올바르게 인식하도록 돕습니다.
        # newline='' 인자는 텍스트를 파일에 쓸 때 불필요한 빈 줄이 생기는 것을 방지합니다.
        with open(filename, 'w', encoding='utf-8-sig', newline='') as file:
            file.write(response.text)
            
        print(f"다운로드 성공! 파일이 '{filename}' 이름으로 저장되었습니다.")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 오류 발생: {http_err}")
        print("URL 주소가 정확한지, 시트의 공유 설정이 '링크가 있는 모든 사용자에게 공개'로 되어 있는지 확인하세요.")
    except requests.exceptions.RequestException as req_err:
        print(f"요청 중 오류 발생: {req_err}")
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")


# 스크립트 실행
if __name__ == "__main__":
    download_sheet_as_csv(sheet_url, output_filename)
