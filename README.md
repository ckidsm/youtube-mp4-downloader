# 유튜브 고음질 다운로더

유튜브 영상에서 고음질 오디오(M4A) 또는 비디오(MP4)를 다운로드하는 파이썬 프로그램입니다.

**두 가지 버전 제공:**
- **GUI 버전** (youtube_ui.py) - PyQt6 기반 사용자 친화적 인터페이스
- **CLI 버전** (youtube_downloader.py) - 명령줄 인터페이스

## 필수 요구사항

### ⚡ 자동 설치 기능

**중요:** 실행 파일 버전은 **FFmpeg와 AtomicParsley를 자동으로 다운로드하고 설치**합니다!

- 첫 실행 시 프로그램이 자동으로 필요한 도구를 다운로드합니다
- 별도의 설치 과정이 필요 없습니다
- 인터넷 연결만 있으면 즉시 사용 가능합니다

### 개발 환경 설정 (소스 빌드 시)

### 1. Python 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. FFmpeg 및 AtomicParsley 설치 (선택사항)
시스템에 직접 설치하고 싶다면:

**macOS (Homebrew):**
```bash
brew install ffmpeg atomicparsley
```

**Windows (Chocolatey):**
```bash
choco install ffmpeg atomicparsley
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg atomicparsley
```

프로그램이 자동으로 다운로드하므로 선택사항입니다.

## 사용 방법

### GUI 버전 (권장)

```bash
# 가상 환경 활성화
source venv/bin/activate

# GUI 프로그램 실행
python youtube_ui.py
```

**GUI 기능:**
- 유튜브 URL 입력 및 **영상 제목 자동 가져오기**
- 저장 경로 및 파일명 설정
- **저장 경로 자동 저장** (다음 실행 시 이전 경로 자동 복원)
- 다운로드 형식 선택 (오디오 M4A, 비디오 MP4 - 최고/720p/480p)
- **고음질 다운로드** (오디오: 320kbps M4A, 비디오: 최대 320kbps AAC)
- **유튜브 썸네일을 앨범 아트로 자동 임베드**
- 다운로드 큐 관리 (여러 영상 동시 다운로드)
- 실시간 진행 상태 표시
- 다운로드 중지/재시작/제거 기능
- **더블클릭으로 파일 재생**
- **마우스 오른쪽 클릭 메뉴** (폴더 열기, 파일 재생)

### CLI 버전

**방법 1: 대화형 모드**
```bash
python youtube_downloader.py
```
프로그램 실행 후 URL과 다운로드 폴더를 입력합니다.

**방법 2: 명령줄 인자**
```bash
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" "저장폴더"
```

## 주요 기능

- **고음질 오디오 다운로드** - M4A 형식 (320kbps, 48kHz)
- **비디오 다운로드** - MP4 형식 (최고화질, 720p, 480p 선택 가능)
- **앨범 아트 자동 임베드** - 유튜브 썸네일을 앨범 커버로 자동 추가
- **자동 파일명 생성** - 영상 제목으로 자동 설정
- **저장 경로 기억** - 마지막으로 사용한 저장 경로를 설정 파일에 저장
- **다운로드 큐 관리** - 여러 영상을 큐에 추가하여 순차/동시 다운로드
- **실시간 진행 상황 표시** - 다운로드 속도, 남은 시간, 진행률
- **사용자 친화적 GUI** - PyQt6 기반의 직관적인 인터페이스

## 예제

```bash
python youtube_downloader.py "https://www.youtube.com/watch?v=JVL3495qUC4"
```

다운로드된 파일은 기본적으로 `downloads` 폴더에 저장됩니다.

## 배포 (실행 파일 빌드)

각 플랫폼에서 실행 파일을 빌드할 수 있습니다.

### macOS
```bash
./build_macos.sh
```
빌드 결과: `dist/YoutubeDownloader.app`

### Windows
```cmd
build_windows.bat
```
빌드 결과: `dist/YoutubeDownloader.exe`

### Linux/Ubuntu
```bash
./build_linux.sh
```
빌드 결과: `dist/YoutubeDownloader`

자세한 빌드 및 설치 방법은 [INSTALL.md](INSTALL.md)를 참고하세요.

## 라이선스

개인 사용 및 학습 목적으로만 사용하세요.
