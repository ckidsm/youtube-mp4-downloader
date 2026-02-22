#!/bin/bash
# Linux/Ubuntu용 빌드 스크립트

echo "=========================================="
echo "Linux용 Youtube Downloader 빌드 시작"
echo "=========================================="

# 현재 디렉토리를 스크립트 위치로 변경
cd "$(dirname "$0")"

# 가상 환경 활성화
echo "가상 환경 활성화 중..."
source venv/bin/activate

# 이전 빌드 정리
echo "이전 빌드 정리 중..."
rm -rf build dist

# PyInstaller로 빌드
echo "PyInstaller로 실행 파일 빌드 중..."
pyinstaller --onefile --windowed \
    --name YoutubeDownloader \
    --add-data "youtube_worker.py:." \
    --add-data "dependency_checker.py:." \
    --hidden-import PyQt6.QtCore \
    --hidden-import PyQt6.QtGui \
    --hidden-import PyQt6.QtWidgets \
    --hidden-import yt_dlp \
    --hidden-import yt_dlp.extractor \
    --hidden-import yt_dlp.postprocessor \
    --hidden-import dependency_checker \
    --hidden-import youtube_worker \
    youtube_ui.py

# 빌드 완료 확인
if [ -f "dist/YoutubeDownloader" ]; then
    echo ""
    echo "=========================================="
    echo "빌드 성공!"
    echo "=========================================="
    echo "실행 파일 위치: dist/YoutubeDownloader"
    echo ""
    echo "다음 명령으로 실행할 수 있습니다:"
    echo "  ./dist/YoutubeDownloader"
    echo ""
    echo "주의: FFmpeg와 AtomicParsley가 시스템에 설치되어 있어야 합니다."
    echo "  sudo apt install ffmpeg atomicparsley"

    # 실행 권한 부여
    chmod +x dist/YoutubeDownloader
else
    echo ""
    echo "=========================================="
    echo "빌드 실패!"
    echo "=========================================="
    exit 1
fi
