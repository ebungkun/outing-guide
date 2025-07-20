# app_font_subsetter_batch.py
# 지정된 폴더 안의 모든 폰트 파일을 한 번에 최적화합니다.
# 폰트의 Bold 속성 플래그를 자동으로 교정하는 기능이 포함되어 있습니다.
#
# 필요 라이브러리 설치:
# pip install fonttools brotli
#
# 사용법:
# python app_font_subsetter_batch.py

import os
import argparse
import glob
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options

def get_characters_from_files(file_paths):
    """
    주어진 파일 목록에서 모든 고유 문자를 추출합니다.
    """
    used_chars = set()
    print("다음 파일들에서 사용된 글자를 수집합니다:")
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                print(f" - {file_path}")
                content = f.read()
                used_chars.update(content)
        except FileNotFoundError:
            print(f"경고: '{file_path}' 파일을 찾을 수 없습니다. 건너뜁니다.")
        except Exception as e:
            print(f"오류: '{file_path}' 파일을 읽는 중 문제가 발생했습니다: {e}")
    
    used_chars.add(' ')
    print(f"\n총 {len(used_chars)}개의 고유한 글자를 수집했습니다.")
    return "".join(sorted(list(used_chars)))

def process_font_file(font_path, subset_text, output_dir):
    """
    단일 폰트 파일을 서브셋팅하고 woff2로 변환하며, bold 속성을 교정합니다.
    """
    print(f"\n--- '{os.path.basename(font_path)}' 처리 중 ---")
    try:
        font = TTFont(font_path)
        
        # --- Bold 속성 플래그 자동 교정 ---
        if 'OS/2' in font and 'head' in font:
            is_bold_in_name = 'bold' in os.path.basename(font_path).lower()
            
            # 현재 Bold 플래그 상태 확인
            selection_bold_is_set = bool(font['OS/2'].fsSelection & (1 << 5))
            macstyle_bold_is_set = bool(font['head'].macStyle & (1 << 0))

            if is_bold_in_name:
                # 파일 이름이 bold를 포함하면, 두 플래그 모두 설정
                if not selection_bold_is_set or not macstyle_bold_is_set:
                    print("Info: 파일 이름에 따라 Bold 속성 플래그를 설정합니다.")
                    font['OS/2'].fsSelection |= (1 << 5)  # BOLD 비트 설정
                    font['head'].macStyle |= (1 << 0)     # BOLD 비트 설정
            else:
                # 파일 이름에 bold가 없으면, 두 플래그 모두 해제
                if selection_bold_is_set or macstyle_bold_is_set:
                    print("Info: 파일 이름에 따라 Bold 속성 플래그를 해제합니다.")
                    font['OS/2'].fsSelection &= ~(1 << 5) # BOLD 비트 해제
                    font['head'].macStyle &= ~(1 << 0)    # BOLD 비트 해제
        # --- 교정 코드 끝 ---

        options = Options()
        options.layout_features = ['*']
        options.glyph_names = True
        options.recalc_bounds = True
        options.recalc_timestamp = True
        options.notdef_outline = True

        subsetter = Subsetter(options)
        subsetter.populate(text=subset_text)
        subsetter.subset(font)

        base_name = os.path.splitext(os.path.basename(font_path))[0]
        woff2_path = os.path.join(output_dir, f"{base_name}_subset.woff2")
        
        font.flavor = 'woff2'
        font.save(woff2_path)
        
        original_size = os.path.getsize(font_path) / 1024
        subset_size = os.path.getsize(woff2_path) / 1024
        
        print(f"결과 파일 생성: {woff2_path}")
        print(f"용량 변화: {original_size:.2f} KB -> {subset_size:.2f} KB")

    except Exception as e:
        print(f"오류: '{os.path.basename(font_path)}' 처리 중 문제가 발생했습니다: {e}")


def main():
    """
    스크립트 실행을 위한 메인 함수
    """
    parser = argparse.ArgumentParser(description="폴더 내의 모든 폰트 파일을 소스 코드 기반으로 일괄 최적화합니다.")
    parser.add_argument("--font-dir", default="./src/assets/fonts/original", help="최적화할 원본 .woff 또는 .ttf 폰트가 있는 폴더")
    parser.add_argument("--source-files", nargs='+', default=["./src/App.jsx", "./src/data/preferences.json"], help="사용된 문자를 추출할 소스 파일 목록")
    parser.add_argument("--output", default="./src/assets/fonts", help="결과물이 저장될 폴더 경로")
    
    args = parser.parse_args()

    subset_text = get_characters_from_files(args.source_files)
    if not subset_text:
        print("오류: 소스 파일에서 추출된 글자가 없어 작업을 중단합니다.")
        return

    if not os.path.exists(args.output):
        print(f"결과물 폴더 '{args.output}'을(를) 생성합니다.")
        os.makedirs(args.output)

    font_files = glob.glob(os.path.join(args.font_dir, '*.woff')) + \
                 glob.glob(os.path.join(args.font_dir, '*.ttf'))

    if not font_files:
        print(f"오류: '{args.font_dir}' 폴더에서 폰트 파일을 찾을 수 없습니다.")
        return

    for font_path in font_files:
        process_font_file(font_path, subset_text, args.output)
    
    print("\n--- 모든 작업 완료 ---")

if __name__ == "__main__":
    main()
