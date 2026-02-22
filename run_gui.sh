#!/bin/bash
# GUI 프로그램 실행 스크립트

# 현재 디렉토리를 스크립트 위치로 변경
cd "$(dirname "$0")"

# 가상 환경 활성화
source venv/bin/activate

# GUI 실행
python youtube_ui.py
