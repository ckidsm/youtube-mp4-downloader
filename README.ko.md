# YouTube 고음질 다운로더

PyQt6 GUI 기반 크로스 플랫폼 YouTube 비디오/오디오 다운로더

---

## 1. 개요

YouTube 고음질 다운로더는 YouTube 비디오에서 고음질 오디오(M4A 320kbps) 또는 비디오(MP4)를 다운로드하는 데스크톱 애플리케이션입니다.

이 시스템은 YouTube 콘텐츠를 로컬에 저장하고 오프라인으로 재생하려는 개인 사용자를 위해 설계되었습니다. 인터넷 연결 없이 음악, 강의, 팟캐스트, 교육 자료 등을 즐기고 싶은 사용자를 대상으로 합니다.

PyQt6 GUI를 통해 사용자는 여러 비디오를 큐에 추가하고 동시에 다운로드할 수 있습니다. 애플리케이션은 YouTube 썸네일을 앨범 아트로 자동 삽입하여 음악 플레이어에서 향상된 시각적 경험을 제공합니다.

시스템은 FFmpeg와 AtomicParsley를 자동으로 다운로드하고 설치하므로 사용자는 추가 설정 없이 프로그램을 바로 실행할 수 있습니다. macOS, Windows, Linux를 지원하며 각 플랫폼에 최적화된 실행 파일을 제공합니다.

---

## 2. 주요 기능

1. **고음질 오디오 다운로드** - M4A 형식 320kbps, 48kHz 샘플링 (`youtube_worker.py`)
2. **다중 화질 비디오 다운로드** - MP4 최고 화질, 720p, 480p 선택 가능 (`youtube_worker.py`)
3. **자동 썸네일 앨범 아트 삽입** - YouTube 썸네일을 메타데이터로 삽입 (`youtube_worker.py`)
4. **자동 의존성 설치** - FFmpeg/AtomicParsley 자동 다운로드 및 설정 (`dependency_checker.py`)
5. **다운로드 큐 관리** - 진행 상황 추적과 함께 여러 동시 다운로드 (`youtube_ui.py`)
6. **자동 제목 추출** - URL에서 비디오 제목 자동 가져오기 및 안전한 파일명 변환 (`youtube_ui.py`)
7. **설정 영속성** - 다운로드 경로 자동 저장 및 복원 (`youtube_ui.py`, `settings.json`)
8. **크로스 플랫폼 빌드** - macOS, Windows, Linux 실행 파일 생성 (`build_*.sh/.bat`)
9. **실시간 진행 상황 표시** - 실시간 다운로드 속도, 예상 시간, 진행률 업데이트 (`youtube_worker.py`)
10. **통합 플레이어** - 완료된 파일 더블클릭으로 즉시 재생 (`youtube_ui.py`)

---

## 3. 개념 / 도메인 모델

### 다운로드 큐
- 사용자가 추가한 다운로드 작업 목록
- 위치: `youtube_ui.py` (QTableWidget)
- 각 항목에는 URL, 저장 경로, 파일명, 형식, 화질, 진행 상태 포함

### 다운로드 워커
- QThread 기반 백그라운드 다운로드 실행 단위
- 위치: `youtube_worker.py` (YoutubeDownloadWorker 클래스)
- 비동기 다운로드, 진행 시그널, 취소 기능 제공

### 다운로드 타입
- 다운로드할 미디어 형식 및 화질
- 위치: `youtube_worker.py` (ydl_opts 설정)
- 타입: audio (M4A 320kbps), video_best, video_720p, video_480p

### 의존성
- 필요한 외부 바이너리 (FFmpeg, AtomicParsley)
- 위치: `dependency_checker.py` (DependencyChecker 클래스)
- 시스템 설치 확인 → 누락 시 자동 다운로드 → 로컬 bin 폴더에 저장

### 설정
- 사용자 환경 설정 (다운로드 경로)
- 위치: `youtube_ui.py` (_load_settings, _save_settings 메서드)
- 저장 위치: `settings.json` (앱 실행 디렉토리)

### 파일 경로 추적
- 실제 다운로드된 파일 경로와 큐 행 간의 매핑
- 위치: `youtube_ui.py` (self.file_paths 딕셔너리)
- yt-dlp가 생성한 실제 파일명과 UI 표시를 연결

---

## 4. 아키텍처

### 구성 요소

**데스크톱 애플리케이션 레이어**
- PyQt6 기반 GUI 애플리케이션 (`youtube_ui.py`)
- 사용자 입력 수신, 다운로드 큐 관리, 진행 상황 표시
- QTableWidget으로 다운로드 목록 관리, 컨텍스트 메뉴 제공

**워커 레이어**
- QThread 기반 비동기 다운로드 워커 (`youtube_worker.py`)
- yt-dlp를 통한 YouTube 비디오 다운로드 실행
- progress, title_resolved, file_path_resolved, finished 시그널을 통해 UI와 통신

**의존성 관리 레이어**
- 자동 의존성 설치 시스템 (`dependency_checker.py`)
- 시스템 환경 확인, 플랫폼별 바이너리 다운로드, PATH 설정

**외부 도구**
- FFmpeg: 오디오/비디오 변환 및 후처리
- AtomicParsley: M4A 메타데이터 및 앨범 아트 삽입
- yt-dlp: YouTube 비디오 다운로드 엔진

### 데이터 흐름

1. **사용자 입력**: URL 입력 → 자동 제목 가져오기 → 큐에 추가
2. **다운로드 시작**: UI에서 항목 선택 → 워커 생성 및 시작
3. **다운로드 진행**: 워커가 yt-dlp 실행 → 진행 시그널 발신 → UI 업데이트
4. **후처리**: FFmpeg 오디오 변환 → AtomicParsley 썸네일 삽입
5. **완료**: 실제 파일 경로 전송 → UI에 완료 표시 → 파일 경로 저장

### 인증/권한 흐름

인증 시스템 없음 (로컬 데스크톱 애플리케이션)

### 설정 영속성 흐름

1. **로드**: 앱 시작 → settings.json 읽기 → 저장 경로 복원
2. **저장**: 사용자가 폴더 선택 → settings.json에 경로 기록

---

## 5. 소스 구조

```
youtubuDn/
├── youtube_ui.py              # 메인 GUI 애플리케이션 (진입점)
│                              # - PyQt6 기반 창 및 위젯 구성
│                              # - 다운로드 큐 관리 (QTableWidget)
│                              # - 워커 생성 및 시그널 연결
│                              # - 컨텍스트 메뉴, 파일 재생, 설정 관리
│
├── youtube_worker.py          # QThread 다운로드 워커
│                              # - yt-dlp 실행 및 진행 추적
│                              # - 플랫폼별 다운로드 옵션
│                              # - 썸네일 삽입 설정
│                              # - 취소 및 타임아웃 처리
│
├── dependency_checker.py      # 자동 의존성 설치 모듈
│                              # - FFmpeg/AtomicParsley 설치 확인
│                              # - 플랫폼별 바이너리 다운로드
│                              # - 로컬 bin 폴더 관리
│                              # - PATH 환경 변수 설정
│
├── youtube_downloader.py      # CLI 버전 다운로더
│                              # - 명령줄 인자 파싱
│                              # - 간단한 다운로드 실행
│
├── youtube_downloader.spec    # PyInstaller 빌드 설정 (macOS)
│                              # - 의존성 및 데이터 파일 지정
│                              # - .app 번들 설정
│
├── build_macos.sh             # macOS 빌드 스크립트
├── build_windows.bat          # Windows 빌드 스크립트
├── build_linux.sh             # Linux 빌드 스크립트
│
├── requirements.txt           # Python 패키지 의존성
│                              # - yt-dlp, PyQt6, pyinstaller
│
├── run_gui.sh                 # 개발 환경 GUI 실행 스크립트
├── README.md                  # 프로젝트 소개 및 사용법 (영문)
├── README.ko.md               # 프로젝트 소개 및 사용법 (한글)
├── INSTALL.md                 # 상세 설치 가이드
└── .gitignore                 # Git 제외 파일 목록
```

### 주요 진입점

- **GUI 버전**: `youtube_ui.py` → `main()` → `YoutubeDownloaderApp` 클래스
- **CLI 버전**: `youtube_downloader.py` → `main()` → `download_youtube_audio()`

### 빌드 출력

- macOS: `dist/YoutubeDownloader.app`
- Windows: `dist/YoutubeDownloader.exe`
- Linux: `dist/YoutubeDownloader`

---

## 6. 작동 방식

### 애플리케이션 시작

1. `youtube_ui.py` 실행 → `main()` 함수 호출
2. `DependencyChecker` 인스턴스 생성 → `check_and_install()` 실행
   - FFmpeg 설치 확인 → 누락 시 자동 다운로드
   - AtomicParsley 설치 확인 → 누락 시 자동 다운로드
   - 로컬 `bin/` 폴더에 저장 → PATH에 추가
3. `QApplication` 및 `YoutubeDownloaderApp` 창 생성
4. `settings.json`에서 저장 경로 로드 → UI에 표시

### 다운로드 요청 흐름

1. **URL 입력 및 제목 가져오기**
   - 사용자가 URL 입력 → "제목 가져오기" 버튼 클릭 (선택 사항)
   - `fetch_video_title()`: yt-dlp로 비디오 정보 추출 → 제목 표시
   - URL 정리: 플레이리스트 파라미터 제거 (`_clean_url()`)

2. **큐에 추가**
   - "큐에 추가" 클릭 → `add_to_queue()` 실행
   - 파일명이 비어있으면 자동으로 제목 가져오기
   - 파일명 정리: 이모지, 특수 문자 제거 (`_sanitize_filename()`)
   - QTableWidget에 새 행 추가 (URL, 경로, 파일명, 형식, 화질, 상태)

3. **다운로드 시작**
   - 사용자가 행 선택 → "선택 항목 다운로드" 클릭
   - `start_selected()`: 선택된 각 행에 대해 `YoutubeDownloadWorker` 생성
   - 워커 시그널 연결:
     - `progress` → UI 진행 상태 업데이트
     - `title_resolved` → 비디오 제목으로 파일명 업데이트
     - `file_path_resolved` → 실제 다운로드 파일 경로 저장
     - `finished` → 완료/실패 처리
   - 워커 스레드 시작 (`worker.start()`)

4. **다운로드 실행 (워커 스레드)**
   - `youtube_worker.py`: `run()` 메서드 실행
   - yt-dlp 옵션 설정 (형식, 화질, 썸네일 삽입)
   - 비디오 정보 추출 → `title_resolved` 시그널 발신
   - 다운로드 실행 → 진행 콜백 → `progress` 시그널 발신
   - FFmpeg 후처리: 오디오 변환, 샘플링 레이트 설정
   - AtomicParsley: 썸네일을 앨범 아트로 삽입
   - 실제 파일 경로 확인 → `file_path_resolved` 시그널 발신
   - `finished` 시그널 발신 (성공/실패)

5. **완료 처리**
   - UI에서 `_on_finished()` 호출
   - 진행 상태를 "✓ 완료" 또는 "✗ 실패"로 업데이트
   - 워커 정리 (`worker.deleteLater()`)

### 파일 재생

1. 사용자가 완료된 행 더블클릭 → `_on_double_click()` 호출
2. `file_paths` 딕셔너리에서 실제 파일 경로 확인
3. 플랫폼별 기본 플레이어로 파일 열기
   - macOS: `open` 명령
   - Windows: `os.startfile()`
   - Linux: `xdg-open` 명령

### 취소 및 제거

1. 사용자가 "선택 항목 중지" 클릭 → `stop_selected()` 실행
2. 워커의 `cancel()` 메서드 호출 → `_is_cancelled` 플래그 설정
3. 2초 타임아웃 대기 → 중지되지 않으면 `terminate()`로 강제 종료
4. 워커 정리 및 UI 상태 업데이트

---

## 7. 설정 및 실행

### 사전 요구 사항

- **Python**: 3.8 이상 (개발: Python 3.13)
- **가상 환경**: venv 권장
- **FFmpeg & AtomicParsley**: 자동 설치 (수동 설치 선택 사항)

### 의존성 설치

```bash
# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Python 패키지 설치
pip install -r requirements.txt
```

### 개발 모드 실행

**GUI 버전:**
```bash
python youtube_ui.py
```

또는:
```bash
chmod +x run_gui.sh
./run_gui.sh
```

**CLI 버전:**
```bash
# 대화형 모드
python youtube_downloader.py

# 명령줄 인자
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" "downloads"
```

### 프로덕션 빌드

**macOS:**
```bash
chmod +x build_macos.sh
./build_macos.sh
# 출력: dist/YoutubeDownloader.app
```

**Windows:**
```cmd
build_windows.bat
REM 출력: dist\YoutubeDownloader.exe
```

**Linux:**
```bash
chmod +x build_linux.sh
./build_linux.sh
# 출력: dist/YoutubeDownloader
```

### 환경 변수

환경 변수 없음 (모든 설정은 `settings.json`에 저장)

### 설정 파일

**settings.json** (앱 실행 디렉토리에 자동 생성)
```json
{
  "download_path": "/Users/username/Downloads"
}
```

---

## 8. 서버 요구 사항 / 사양

이 프로젝트는 **로컬 데스크톱 애플리케이션**으로 서버 요구 사항이 없습니다.

### 클라이언트 요구 사항

**필요한 포트**: 없음 (로컬 실행)

**메모리 요구 사항**:
- 최소: 512MB (Python + PyQt6)
- 권장: 1GB 이상 (다중 다운로드용)

**CPU 요구 사항**:
- 최소: 1 코어 (단일 다운로드)
- 권장: 2 코어 이상 (다중 다운로드)

**저장 공간 요구 사항**:
- 앱 크기: ~50MB (빌드된 실행 파일)
- 다운로드 공간: 사용자의 다운로드 파일 크기에 따라 다름
- 로그: 없음 (콘솔 출력만)

**네트워크 요구 사항**:
- 인터넷 연결 필요 (YouTube 다운로드 및 자동 의존성 설치)

---

## 9. 운영

### 로깅

**위치**: 표준 출력 (콘솔)
**레벨**: `print()` 문을 통한 정보 메시지
**내용**:
- 의존성 확인 결과
- 다운로드 진행 상태
- 오류 메시지

개발 모드에서는 터미널에 출력되고, 빌드된 앱에서는 시스템 로그에 출력되거나 무시됩니다.

### 상태 확인

상태 확인 엔드포인트 없음 (데스크톱 애플리케이션)

### 백업 및 마이그레이션

**백업 대상**:
- `settings.json`: 사용자 저장 경로 설정
- 다운로드된 파일: 사용자 지정 폴더

**마이그레이션**: 없음 (데이터베이스 없음)

### 배포 방법

**빌드 도구**: PyInstaller
- `youtube_downloader.spec` (macOS)
- `build_macos.sh`, `build_windows.bat`, `build_linux.sh`

**배포 프로세스**:
1. 각 플랫폼에서 빌드 스크립트 실행
2. `dist/` 폴더에서 실행 파일 배포
3. 사용자는 다운로드하여 실행만 하면 됨

**업데이트**:
- 수동 업데이트 (새 버전 다운로드 및 교체)
- 자동 업데이트 기능 없음

---

## 10. 보안 사항

### 인증/세션

인증 시스템 없음 (로컬 애플리케이션)

### 권한

**파일 시스템 권한**:
- 사용자가 선택한 폴더에 대한 쓰기 권한 필요
- macOS: 첫 실행 시 "폴더 접근" 권한 요청 가능

**네트워크 권한**:
- YouTube 서버 접근
- 의존성 다운로드 서버 접근 (evermeet.cx, gyan.dev, johnvansickle.com, GitHub)

### 입력 유효성 검사

**URL 유효성 검사**:
- `_clean_url()`: URL 파싱 및 불필요한 파라미터 제거 (`youtube_ui.py:190-221`)
- yt-dlp가 잘못된 URL 거부

**파일명 유효성 검사**:
- `_sanitize_filename()`: 특수 문자, 이모지, 경로 구분자 제거 (`youtube_ui.py:321-354`)
- 파일명 길이 제한 (200자)

### 민감 정보/시크릿 처리

민감 정보 없음

**저장 정보**:
- `settings.json`: 저장 경로만 포함 (평문)
- 다운로드된 파일: 사용자 선택 폴더

### 코드 서명

**macOS**: `youtube_downloader.spec`에서 `codesign_identity=None` (서명 없음)
**Windows**: 서명 없음
**Linux**: 서명 없음

사용자는 "미확인 개발자" 경고를 수동으로 승인해야 할 수 있습니다.

---

## 11. 문제 해결

### macOS: "미확인 개발자" 경고

**문제**: 앱 실행 시 보안 경고
**해결 방법**:
```bash
xattr -cr /path/to/YoutubeDownloader.app
```
또는 시스템 설정 > 개인 정보 보호 및 보안 > 보안 > "확인 없이 열기"

### Windows: "Windows Defender" 경고

**문제**: SmartScreen 경고
**해결 방법**: "추가 정보" 클릭 → "실행"

### 앨범 아트가 표시되지 않음

**문제**: AtomicParsley가 설치되지 않음
**확인**:
```bash
# macOS/Linux
which AtomicParsley

# Windows
where AtomicParsley
```
**해결 방법**: 프로그램 재시작 (자동 다운로드) 또는 수동 설치

### 다운로드가 멈춤

**문제**: 네트워크 타임아웃 또는 YouTube 제한
**해결 방법**:
1. "선택 항목 중지" 클릭
2. 항목 제거 후 재시도
3. URL 확인 (단일 비디오, 플레이리스트 아님)

### 파일을 찾을 수 없음 (더블클릭 시)

**문제**: 다운로드 경로 변경 또는 파일 삭제
**해결 방법**:
1. 컨텍스트 메뉴 → "다운로드 폴더 열기"
2. 파일 수동 확인
3. 파일이 없으면 재다운로드

### Python 버전 오류

**문제**: Python 3.7 이하 사용
**해결 방법**: Python 3.8 이상 설치
```bash
python3 --version
```

---

## 12. 라이선스 / 면책 조항

**라이선스**: 명시되지 않음

**사용 목적**: 개인 사용 및 교육 목적으로만 사용

**면책 조항**:
- 이 소프트웨어는 YouTube 콘텐츠 다운로드 도구입니다
- 사용자는 YouTube 서비스 약관을 준수할 책임이 있습니다
- 허가 없이 저작권이 있는 콘텐츠를 다운로드하지 마십시오
- 개발자는 이 소프트웨어의 오용으로 인한 법적 문제에 대해 책임을 지지 않습니다

**기여**: GitHub Issues 및 Pull Requests를 통한 기여 환영

**연락처**: GitHub Issues 페이지 사용

---

## 빠른 시작

```bash
# 저장소 클론
git clone https://github.com/ckidsm/youtube-mp4-downloader.git
cd youtube-mp4-downloader

# 가상 환경 설정
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# GUI 실행
python youtube_ui.py

# 빌드 (macOS 예시)
./build_macos.sh
```

---

## 스크린샷

다운로드 큐 관리, 실시간 진행 상황 표시, 통합 파일 플레이어가 있는 GUI 애플리케이션.

---

## 크레딧

다음 기술로 제작:
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI 프레임워크
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube 다운로드 엔진
- [FFmpeg](https://ffmpeg.org/) - 오디오/비디오 처리
- [AtomicParsley](https://github.com/wez/atomicparsley) - 메타데이터 처리
- [PyInstaller](https://www.pyinstaller.org/) - 실행 파일 빌더
