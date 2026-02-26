#!/bin/bash
# macOS용 빌드 스크립트

echo "=========================================="
echo "macOS용 Youtube Downloader 빌드 시작"
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
echo "PyInstaller로 앱 빌드 중..."
pyinstaller youtube_downloader.spec

# 빌드 완료 확인
if [ -d "dist/YoutubeDownloader.app" ]; then
    echo ""
    echo "필수 바이너리 설치 중..."

    # bin 디렉토리 생성
    BIN_DIR="dist/YoutubeDownloader.app/Contents/MacOS/bin"
    mkdir -p "$BIN_DIR"

    # 시스템에서 FFmpeg와 AtomicParsley 복사 (Homebrew 설치된 경우)
    if [ -f "/opt/homebrew/bin/ffmpeg" ]; then
        echo "  ✓ FFmpeg 복사 중 (Homebrew ARM64 버전)..."
        cp "/opt/homebrew/bin/ffmpeg" "$BIN_DIR/"
        chmod 755 "$BIN_DIR/ffmpeg"
        xattr -cr "$BIN_DIR/ffmpeg" 2>/dev/null || true
        echo "  ✓ FFmpeg 설치 완료"
    elif [ -f "/usr/local/bin/ffmpeg" ]; then
        echo "  ✓ FFmpeg 복사 중 (Homebrew Intel 버전)..."
        cp "/usr/local/bin/ffmpeg" "$BIN_DIR/"
        chmod 755 "$BIN_DIR/ffmpeg"
        xattr -cr "$BIN_DIR/ffmpeg" 2>/dev/null || true
        echo "  ✓ FFmpeg 설치 완료"
    else
        echo "  ⚠ FFmpeg가 시스템에 설치되지 않았습니다."
        echo "    첫 실행 시 자동으로 다운로드됩니다."
    fi

    if [ -f "/opt/homebrew/bin/AtomicParsley" ]; then
        echo "  ✓ AtomicParsley 복사 중 (Homebrew ARM64 버전)..."
        cp "/opt/homebrew/bin/AtomicParsley" "$BIN_DIR/"
        chmod 755 "$BIN_DIR/AtomicParsley"
        xattr -cr "$BIN_DIR/AtomicParsley" 2>/dev/null || true
        echo "  ✓ AtomicParsley 설치 완료"
    elif [ -f "/usr/local/bin/AtomicParsley" ]; then
        echo "  ✓ AtomicParsley 복사 중 (Homebrew Intel 버전)..."
        cp "/usr/local/bin/AtomicParsley" "$BIN_DIR/"
        chmod 755 "$BIN_DIR/AtomicParsley"
        xattr -cr "$BIN_DIR/AtomicParsley" 2>/dev/null || true
        echo "  ✓ AtomicParsley 설치 완료"
    else
        echo "  ⚠ AtomicParsley가 시스템에 설치되지 않았습니다."
        echo "    첫 실행 시 자동으로 다운로드됩니다."
    fi

    # 앱 번들 자체의 quarantine 속성도 제거
    echo ""
    echo "코드 서명 및 보안 속성 정리 중..."
    xattr -cr "dist/YoutubeDownloader.app" 2>/dev/null || true
    echo "  ✓ 완료"

    echo ""
    echo "=========================================="
    echo "빌드 성공!"
    echo "=========================================="
    echo "실행 파일 위치: dist/YoutubeDownloader.app"
    echo ""
    echo "다음 명령으로 실행할 수 있습니다:"
    echo "  open dist/YoutubeDownloader.app"
    echo ""
    if [ -f "$BIN_DIR/ffmpeg" ] && [ -f "$BIN_DIR/AtomicParsley" ]; then
        echo "✓ FFmpeg와 AtomicParsley가 앱 번들에 포함되었습니다."
    else
        echo "⚠ FFmpeg 또는 AtomicParsley를 시스템에 설치하세요:"
        echo "  brew install ffmpeg atomicparsley"
    fi
else
    echo ""
    echo "=========================================="
    echo "빌드 실패!"
    echo "=========================================="
    exit 1
fi
