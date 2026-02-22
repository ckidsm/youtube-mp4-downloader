@echo off
REM Windows용 빌드 스크립트

echo ==========================================
echo Windows용 Youtube Downloader 빌드 시작
echo ==========================================

REM 현재 디렉토리로 이동
cd /d %~dp0

REM 가상 환경 활성화
echo 가상 환경 활성화 중...
call venv\Scripts\activate.bat

REM 이전 빌드 정리
echo 이전 빌드 정리 중...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM PyInstaller로 빌드
echo PyInstaller로 실행 파일 빌드 중...
pyinstaller --onefile --windowed ^
    --name YoutubeDownloader ^
    --add-data "youtube_worker.py;." ^
    --add-data "dependency_checker.py;." ^
    --hidden-import PyQt6.QtCore ^
    --hidden-import PyQt6.QtGui ^
    --hidden-import PyQt6.QtWidgets ^
    --hidden-import yt_dlp ^
    --hidden-import yt_dlp.extractor ^
    --hidden-import yt_dlp.postprocessor ^
    --hidden-import dependency_checker ^
    --hidden-import youtube_worker ^
    youtube_ui.py

REM 빌드 완료 확인
if exist dist\YoutubeDownloader.exe (
    echo.
    echo ==========================================
    echo 빌드 성공!
    echo ==========================================
    echo 실행 파일 위치: dist\YoutubeDownloader.exe
    echo.
    echo 주의: FFmpeg와 AtomicParsley가 시스템에 설치되어 있어야 합니다.
    echo   choco install ffmpeg atomicparsley
) else (
    echo.
    echo ==========================================
    echo 빌드 실패!
    echo ==========================================
    exit /b 1
)

pause
