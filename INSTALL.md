# Youtube Downloader 설치 가이드

## 목차
1. [macOS 설치](#macos-설치)
2. [Windows 설치](#windows-설치)
3. [Ubuntu/Linux 설치](#ubuntulinux-설치)
4. [필수 요구사항](#필수-요구사항)
5. [빌드 방법](#빌드-방법)

---

## macOS 설치

### 방법 1: 실행 파일 다운로드 (권장)

1. `dist/YoutubeDownloader.app` 파일을 Applications 폴더로 복사
2. YoutubeDownloader.app을 실행
3. 첫 실행 시 FFmpeg와 AtomicParsley가 자동으로 다운로드됩니다 (인터넷 연결 필요)

**선택사항:** 시스템에 직접 설치하려면:
```bash
brew install ffmpeg atomicparsley
```

### 방법 2: 소스에서 빌드

1. 저장소 클론:
   ```bash
   git clone <repository-url>
   cd youtubuDn
   ```

2. Python 가상 환경 생성 및 의존성 설치:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. 필수 도구 설치:
   ```bash
   brew install ffmpeg atomicparsley
   ```

4. 빌드 실행:
   ```bash
   chmod +x build_macos.sh
   ./build_macos.sh
   ```

5. 빌드된 앱 실행:
   ```bash
   open dist/YoutubeDownloader.app
   ```

### 보안 설정

처음 실행 시 "확인되지 않은 개발자" 경고가 표시될 수 있습니다:
1. 시스템 설정 > 개인 정보 보호 및 보안 > 보안
2. "확인 없이 열기" 버튼 클릭

---

## Windows 설치

### 방법 1: 실행 파일 다운로드 (권장)

1. `dist/YoutubeDownloader.exe` 파일 다운로드
2. YoutubeDownloader.exe 실행
3. 첫 실행 시 FFmpeg와 AtomicParsley가 자동으로 다운로드됩니다 (인터넷 연결 필요)

**선택사항:** 시스템에 직접 설치하려면 (관리자 권한 PowerShell):
```powershell
choco install ffmpeg atomicparsley
```

### 방법 2: 소스에서 빌드

1. Python 3.8 이상 설치
2. 저장소 클론:
   ```cmd
   git clone <repository-url>
   cd youtubuDn
   ```

3. Python 가상 환경 생성 및 의존성 설치:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   pip install pyinstaller
   ```

4. 필수 도구 설치:
   ```cmd
   choco install ffmpeg atomicparsley
   ```

5. 빌드 실행:
   ```cmd
   build_windows.bat
   ```

6. 빌드된 실행 파일:
   ```
   dist\YoutubeDownloader.exe
   ```

### Windows Defender 경고

Windows Defender가 경고를 표시할 수 있습니다:
1. "추가 정보" 클릭
2. "실행" 버튼 클릭

---

## Ubuntu/Linux 설치

### 방법 1: 실행 파일 다운로드 (권장)

1. `dist/YoutubeDownloader` 파일 다운로드
2. 실행 권한 부여:
   ```bash
   chmod +x YoutubeDownloader
   ```
3. 실행:
   ```bash
   ./YoutubeDownloader
   ```
4. 첫 실행 시 FFmpeg와 AtomicParsley가 자동으로 다운로드됩니다 (인터넷 연결 필요)

**선택사항:** 시스템에 직접 설치하려면:
```bash
sudo apt update
sudo apt install ffmpeg atomicparsley
```

### 방법 2: 소스에서 빌드

1. Python 3.8 이상 설치:
   ```bash
   sudo apt update
   sudo apt install python3 python3-venv python3-pip git
   ```

2. 저장소 클론:
   ```bash
   git clone <repository-url>
   cd youtubuDn
   ```

3. Python 가상 환경 생성 및 의존성 설치:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install pyinstaller
   ```

4. 필수 도구 설치:
   ```bash
   sudo apt install ffmpeg atomicparsley
   ```

5. 빌드 실행:
   ```bash
   chmod +x build_linux.sh
   ./build_linux.sh
   ```

6. 빌드된 실행 파일:
   ```bash
   ./dist/YoutubeDownloader
   ```

### 데스크탑 통합 (선택사항)

데스크탑 아이콘 생성을 원한다면 `.desktop` 파일 생성:

```bash
cat > ~/.local/share/applications/youtube-downloader.desktop <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Youtube Downloader
Comment=고음질 유튜브 다운로더
Exec=/path/to/YoutubeDownloader
Terminal=false
Categories=AudioVideo;
EOF
```

---

## 필수 요구사항

### ⚡ 자동 설치 기능

**중요:** 이 프로그램은 **FFmpeg와 AtomicParsley를 자동으로 다운로드하고 설치**합니다!

첫 실행 시 프로그램이 자동으로:
1. FFmpeg와 AtomicParsley가 시스템에 설치되어 있는지 확인
2. 설치되지 않은 경우 자동으로 다운로드
3. 앱 내부 `bin/` 폴더에 저장
4. 즉시 사용 가능하도록 설정

**사용자가 별도로 설치할 필요 없습니다!**

### 모든 플랫폼 공통

1. **FFmpeg** - 오디오/비디오 변환 (자동 설치)
2. **AtomicParsley** - M4A 앨범 아트 임베딩 (자동 설치)
3. **Python 3.8+** (소스 빌드 시만 필요)

### 플랫폼별 요구사항

#### macOS
- macOS 10.13 (High Sierra) 이상
- Homebrew (권장)

#### Windows
- Windows 10 이상
- Chocolatey (권장)

#### Ubuntu/Linux
- Ubuntu 20.04 이상 (또는 동등한 배포판)
- apt 패키지 매니저

---

## 빌드 방법

각 플랫폼에서 빌드를 수행해야 합니다. 크로스 컴파일은 지원되지 않습니다.

### macOS에서 빌드
```bash
./build_macos.sh
```

### Windows에서 빌드
```cmd
build_windows.bat
```

### Linux에서 빌드
```bash
./build_linux.sh
```

### 빌드 출력

빌드가 성공하면 `dist/` 디렉토리에 다음 파일이 생성됩니다:
- **macOS**: `YoutubeDownloader.app` (앱 번들)
- **Windows**: `YoutubeDownloader.exe` (실행 파일)
- **Linux**: `YoutubeDownloader` (실행 파일)

---

## 문제 해결

### macOS: "손상된 파일" 오류
```bash
xattr -cr dist/YoutubeDownloader.app
```

### Windows: "VCRUNTIME140.dll 누락" 오류
Microsoft Visual C++ 재배포 가능 패키지 설치:
https://aka.ms/vs/17/release/vc_redist.x64.exe

### Linux: "Qt platform plugin 오류"
```bash
sudo apt install libxcb-xinerama0
```

### 앨범 아트가 표시되지 않음
AtomicParsley가 설치되어 있는지 확인:
```bash
# macOS
which AtomicParsley

# Windows
where AtomicParsley

# Linux
which AtomicParsley
```

---

## 지원

문제가 발생하면 GitHub Issues에 보고해주세요.

## 라이선스

개인 사용 및 학습 목적으로만 사용하세요.
