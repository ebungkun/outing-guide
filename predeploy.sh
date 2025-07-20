#!/bin/bash
set -e # 스크립트 실행 중 오류가 발생하면 즉시 중단

echo "🚀 데이터 다운로드를 시작합니다..."
uv run download_data.py

echo "📄 CSV를 JSON으로 변환합니다..."
uv run convert_csv_to_json.py

echo "✒️ 폰트를 최적화합니다..."
uv run optimize_font.py

echo "✅ 모든 사전 작업 완료!"