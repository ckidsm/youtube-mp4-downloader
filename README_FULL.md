# YouTube 고음질 다운로더

PyQt6 기반 크로스 플랫폼 유튜브 영상/오디오 다운로더

---

## 1. Overview

YouTube 고음질 다운로더는 유튜브 영상에서 고품질 오디오(M4A 320kbps) 또는 비디오(MP4)를 다운로드하는 데스크톱 애플리케이션입니다.

이 시스템은 개인 사용자가 유튜브 콘텐츠를 로컬에 저장하고 오프라인에서 재생할 수 있도록 설계되었습니다. 음악 강의, 팟캐스트, 교육 자료 등을 인터넷 연결 없이 감상하고자 하는 사용자를 대상으로 합니다.

PyQt6 GUI를 통해 여러 영상을 큐에 추가하고 동시에 다운로드할 수 있으며, 유튜브 썸네일을 자동으로 앨범 아트로 임베딩하여 음악 플레이어에서 시각적으로 향상된 경험을 제공합니다.

시스템은 FFmpeg와 AtomicParsley를 자동으로 다운로드하고 설치하므로 사용자가 별도의 설정 없이 프로그램을 실행하면 즉시 사용할 수 있습니다. macOS, Windows, Linux를 모두 지원하며 각 플랫폼에 최적화된 실행 파일을 제공합니다.

---

## 2. Key Features

1. **고음질 오디오 다운로드** - M4A 형식 320kbps, 48kHz 샘플링 (`youtube_worker.py`)
2. **다중 화질 비디오 다운로드** - MP4 최고화질, 720p, 480p 선택 가능 (`youtube_worker.py`)
3. **썸네일 앨범 아트 자동 임베딩** - 유튜브 썸네일을 메타데이터로 포함 (`youtube_worker.py`)
4. **의존성 자동 설치** - FFmpeg/AtomicParsley 자동 다운로드 및 설정 (`dependency_checker.py`)
5. **다운로드 큐 관리** - 여러 영상 동시 다운로드 및 진행 상태 추적 (`youtube_ui.py`)
6. **자동 제목 추출** - URL에서 영상 제목 자동 가져오기 및 안전한 파일명 변환 (`youtube_ui.py`)
7. **설정 영속성** - 저장 경로 자동 저장 및 복원 (`youtube_ui.py`, `settings.json`)
8. **크로스 플랫폼 빌드** - macOS, Windows, Linux 실행 파일 생성 (`build_*.sh/.bat`)
9. **실시간 진행 표시** - 다운로드 속도, ETA, 진행률 실시간 업데이트 (`youtube_worker.py`)
10. **통합 플레이어** - 더블클릭으로 다운로드 완료 파일 즉시 재생 (`youtube_ui.py`)

---

## 3. Concepts / Domain Model

### Download Queue (다운로드 큐)
- 사용자가 추가한 다운로드 작업 목록
- 위치: `youtube_ui.py` (QTableWidget)
- 각 항목은 URL, 저장 경로, 파일명, 형식, 음질, 진행 상태 포함

### Download Worker (다운로드 워커)
- QThread 기반 백그라운드 다운로드 실행 단위
- 위치: `youtube_worker.py` (YoutubeDownloadWorker 클래스)
- 비동기 다운로드, 진행 상태 시그널 발생, 취소 기능 제공

### Download Type (다운로드 형식)
- 다운로드할 미디어 형식 및 품질
- 위치: `youtube_worker.py` (ydl_opts 설정)
- 종류: audio (M4A 320kbps), video_best, video_720p, video_480p

### Dependency (의존성)
- 필수 외부 바이너리 (FFmpeg, AtomicParsley)
- 위치: `dependency_checker.py` (DependencyChecker 클래스)
- 시스템 설치 확인 → 미설치 시 자동 다운로드 → 로컬 bin 폴더 저장

### Settings (설정)
- 사용자 환경 설정 (저장 경로)
- 위치: `youtube_ui.py` (_load_settings, _save_settings 메서드)
- 저장 위치: `settings.json` (앱 실행 디렉토리)

### File Path Tracking (파일 경로 추적)
- 다운로드된 실제 파일 경로와 큐 행 매핑
- 위치: `youtube_ui.py` (self.file_paths 딕셔너리)
- yt-dlp가 생성한 실제 파일명과 UI 표시 연결

---

## 4. Architecture

### 구성 요소

**Desktop Application Layer**
- PyQt6 기반 GUI 애플리케이션 (`youtube_ui.py`)
- 사용자 입력 수신, 다운로드 큐 관리, 진행 상태 표시
- QTableWidget으로 다운로드 목록 관리, 컨텍스트 메뉴 제공

**Worker Layer**
- QThread 기반 비동기 다운로드 워커 (`youtube_worker.py`)
- yt-dlp를 통한 YouTube 영상 다운로드 실행
- progress, title_resolved, file_path_resolved, finished 시그널로 UI와 통신

**Dependency Management Layer**
- 의존성 자동 설치 시스템 (`dependency_checker.py`)
- 시스템 환경 확인, 플랫폼별 바이너리 다운로드, PATH 설정

**External Tools**
- FFmpeg: 오디오/비디오 변환 및 후처리
- AtomicParsley: M4A 메타데이터 및 앨범 아트 임베딩
- yt-dlp: YouTube 영상 다운로드 엔진

### 데이터 흐름

1. **사용자 입력**: URL 입력 → 제목 자동 가져오기 → 큐에 추가
2. **다운로드 시작**: UI에서 선택 항목 다운로드 → Worker 생성 및 시작
3. **다운로드 진행**: Worker가 yt-dlp 실행 → 진행 상태 시그널 발생 → UI 업데이트
4. **후처리**: FFmpeg로 오디오 변환 → AtomicParsley로 썸네일 임베딩
5. **완료**: 실제 파일 경로 전송 → UI에 완료 표시 → 파일 경로 저장

### 인증/권한 흐름

인증 시스템 없음 (로컬 데스크톱 애플리케이션)

### 설정 영속성 흐름

1. **로드**: 앱 시작 → settings.json 읽기 → 저장 경로 복원
2. **저장**: 사용자가 폴더 선택 → settings.json에 경로 기록

---

## 5. Source Structure (소스 구조 분석)

```
youtubuDn/
├── youtube_ui.py              # 메인 GUI 애플리케이션 (엔트리포인트)
│                              # - PyQt6 기반 윈도우 및 위젯 구성
│                              # - 다운로드 큐 관리 (QTableWidget)
│                              # - 워커 생성 및 시그널 연결
│                              # - 컨텍스트 메뉴, 파일 재생, 설정 관리
│
├── youtube_worker.py          # QThread 다운로드 워커
│                              # - yt-dlp 실행 및 진행 상태 추적
│                              # - 플랫폼별 다운로드 옵션 설정
│                              # - 썸네일 임베딩 설정
│                              # - 취소 및 타임아웃 처리
│
├── dependency_checker.py      # 의존성 자동 설치 모듈
│                              # - FFmpeg/AtomicParsley 설치 확인
│                              # - 플랫폼별 바이너리 다운로드
│                              # - 로컬 bin 폴더 관리
│                              # - PATH 환경변수 설정
│
├── youtube_downloader.py      # CLI 버전 다운로더
│                              # - 명령줄 인자 파싱
│                              # - 단순 다운로드 실행
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
├── README.md                  # 프로젝트 소개 및 사용법
├── INSTALL.md                 # 상세 설치 가이드
└── .gitignore                 # Git 제외 파일 목록
```

### 주요 엔트리포인트

- **GUI 버전**: `youtube_ui.py` → `main()` → `YoutubeDownloaderApp` 클래스
- **CLI 버전**: `youtube_downloader.py` → `main()` → `download_youtube_audio()`

### 빌드 출력

- macOS: `dist/YoutubeDownloader.app`
- Windows: `dist/YoutubeDownloader.exe`
- Linux: `dist/YoutubeDownloader`

---

## 6. How It Works (동작 원리)

### 애플리케이션 시작

1. `youtube_ui.py` 실행 → `main()` 함수 호출
2. `DependencyChecker` 인스턴스 생성 → `check_and_install()` 실행
   - FFmpeg 설치 확인 → 미설치 시 자동 다운로드
   - AtomicParsley 설치 확인 → 미설치 시 자동 다운로드
   - 로컬 `bin/` 폴더에 저장 → PATH에 추가
3. `QApplication` 및 `YoutubeDownloaderApp` 윈도우 생성
4. `settings.json`에서 저장 경로 로드 → UI에 표시

### 다운로드 요청 흐름

1. **URL 입력 및 제목 가져오기**
   - 사용자가 URL 입력 → "제목 가져오기" 버튼 클릭 (선택)
   - `fetch_video_title()`: yt-dlp로 영상 정보 추출 → 제목 표시
   - URL 정리: 플레이리스트 파라미터 제거 (`_clean_url()`)

2. **큐에 추가**
   - "큐에 추가" 버튼 클릭 → `add_to_queue()` 실행
   - 파일명이 없으면 자동으로 제목 가져오기
   - 파일명 정제: 이모지, 특수문자 제거 (`_sanitize_filename()`)
   - QTableWidget에 새 행 추가 (URL, 경로, 파일명, 형식, 음질, 상태)

3. **다운로드 시작**
   - 사용자가 행 선택 → "선택 항목 다운로드" 버튼 클릭
   - `start_selected()`: 선택된 행마다 `YoutubeDownloadWorker` 생성
   - 워커 시그널 연결:
     - `progress` → UI 진행 상태 업데이트
     - `title_resolved` → 영상 제목으로 파일명 업데이트
     - `file_path_resolved` → 실제 다운로드 파일 경로 저장
     - `finished` → 완료/실패 처리
   - 워커 스레드 시작 (`worker.start()`)

4. **다운로드 실행 (워커 스레드)**
   - `youtube_worker.py`: `run()` 메서드 실행
   - yt-dlp 옵션 설정 (형식, 품질, 썸네일 임베딩)
   - 영상 정보 추출 → `title_resolved` 시그널 발생
   - 다운로드 실행 → 진행 상태 콜백 → `progress` 시그널 발생
   - FFmpeg 후처리: 오디오 변환, 샘플링 레이트 설정
   - AtomicParsley: 썸네일을 앨범 아트로 임베딩
   - 실제 파일 경로 확인 → `file_path_resolved` 시그널 발생
   - `finished` 시그널 발생 (성공/실패)

5. **완료 처리**
   - UI에서 `_on_finished()` 호출
   - 진행 상태를 "✓ 완료" 또는 "✗ 실패" 업데이트
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
3. 2초 타임아웃 대기 → 워커가 종료되지 않으면 `terminate()` 강제 종료
4. 워커 정리 및 UI 상태 업데이트

---

## 7. Setup & Run (로컬 실행)

### 사전 요구사항

- **Python**: 3.8 이상 (개발: Python 3.13)
- **가상 환경**: venv 권장
- **FFmpeg & AtomicParsley**: 자동 설치되므로 선택사항

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
# 결과: dist/YoutubeDownloader.app
```

**Windows:**
```cmd
build_windows.bat
REM 결과: dist\YoutubeDownloader.exe
```

**Linux:**
```bash
chmod +x build_linux.sh
./build_linux.sh
# 결과: dist/YoutubeDownloader
```

### 환경 변수

환경 변수 없음 (모든 설정은 `settings.json`에 저장)

### 설정 파일

**settings.json** (자동 생성, 앱 실행 디렉토리)
```json
{
  "download_path": "/Users/username/Downloads"
}
```

---

## 8. Server Requirements / Spec (서버 사양)

이 프로젝트는 **로컬 데스크톱 애플리케이션**으로 서버 요구사항이 없습니다.

### 클라이언트 요구사항

**필요 포트**: 없음 (로컬 실행)

**메모리 요구사항**:
- 최소: 512MB (Python + PyQt6)
- 권장: 1GB 이상 (다중 다운로드 시)

**CPU 요구사항**:
- 최소: 1 코어 (단일 다운로드)
- 권장: 2 코어 이상 (다중 다운로드)

**스토리지 요구사항**:
- 앱 크기: ~50MB (빌드된 실행 파일)
- 다운로드 공간: 사용자가 다운로드하는 파일 크기에 따라 다름
- 로그: 없음 (콘솔 출력만)

**네트워크 요구사항**:
- 인터넷 연결 필요 (YouTube 다운로드 및 의존성 자동 설치)

---

## 9. Operations (운영 구조)

### 로그

**위치**: 표준 출력 (콘솔)
**레벨**: `print()` 문을 통한 정보성 메시지
**내용**:
- 의존성 확인 결과
- 다운로드 진행 상태
- 오류 메시지

개발 모드에서는 터미널에 출력되며, 빌드된 앱에서는 시스템 로그 또는 무시됩니다.

### 헬스체크

헬스체크 엔드포인트 없음 (데스크톱 애플리케이션)

### 백업 및 마이그레이션

**백업 대상**:
- `settings.json`: 사용자 저장 경로 설정
- 다운로드된 파일: 사용자가 지정한 폴더

**마이그레이션**: 없음 (데이터베이스 없음)

### 배포 방식

**빌드 도구**: PyInstaller
- `youtube_downloader.spec` (macOS)
- `build_macos.sh`, `build_windows.bat`, `build_linux.sh`

**배포 방법**:
1. 각 플랫폼에서 빌드 스크립트 실행
2. `dist/` 폴더의 실행 파일 배포
3. 사용자는 다운로드하여 실행만 하면 됨

**업데이트**:
- 수동 업데이트 (새 버전 다운로드 및 교체)
- 자동 업데이트 기능 없음

---

## 10. Security Notes

### 인증/세션

인증 시스템 없음 (로컬 애플리케이션)

### 권한

**파일 시스템 권한**:
- 사용자가 선택한 폴더에 쓰기 권한 필요
- macOS: 첫 실행 시 "폴더 접근" 권한 요청 가능

**네트워크 권한**:
- YouTube 서버 접근
- 의존성 다운로드 서버 접근 (evermeet.cx, gyan.dev, johnvansickle.com, GitHub)

### 입력 검증

**URL 검증**:
- `_clean_url()`: URL 파싱 및 불필요한 파라미터 제거 (`youtube_ui.py:190-221`)
- yt-dlp가 유효하지 않은 URL 거부

**파일명 검증**:
- `_sanitize_filename()`: 특수문자, 이모지, 경로 구분자 제거 (`youtube_ui.py:321-354`)
- 파일명 길이 제한 (200자)

### 민감정보/Secrets 처리

민감정보 없음

**저장되는 정보**:
- `settings.json`: 저장 경로만 포함 (평문)
- 다운로드 파일: 사용자 선택 폴더

### 코드 서명

**macOS**: `youtube_downloader.spec`에서 `codesign_identity=None` (서명 없음)
**Windows**: 서명 없음
**Linux**: 서명 없음

사용자는 "확인되지 않은 개발자" 경고를 수동으로 승인해야 할 수 있습니다.

---

## 11. Troubleshooting

### macOS: "확인되지 않은 개발자" 경고

**문제**: 앱 실행 시 보안 경고
**해결**:
```bash
xattr -cr /path/to/YoutubeDownloader.app
```
또는 시스템 설정 > 보안 > "확인 없이 열기"

### Windows: "Windows Defender" 경고

**문제**: SmartScreen 경고
**해결**: "추가 정보" → "실행" 클릭

### 앨범 아트가 표시되지 않음

**문제**: AtomicParsley가 설치되지 않음
**확인**:
```bash
# macOS/Linux
which AtomicParsley

# Windows
where AtomicParsley
```
**해결**: 프로그램 재시작 (자동 다운로드) 또는 수동 설치

### 다운로드가 멈춤

**문제**: 네트워크 타임아웃 또는 YouTube 제한
**해결**:
1. "선택 항목 중지" 클릭
2. 항목 제거 후 재시도
3. URL 확인 (플레이리스트가 아닌 단일 영상인지)

### 파일을 찾을 수 없음 (더블클릭 시)

**문제**: 다운로드 경로가 변경되었거나 파일이 삭제됨
**해결**:
1. 컨텍스트 메뉴 → "다운로드 폴더 열기"
2. 파일 수동으로 확인
3. 파일이 없으면 재다운로드

### Python 버전 오류

**문제**: Python 3.7 이하 사용
**해결**: Python 3.8 이상 설치
```bash
python3 --version
```

---

## 12. License / Disclaimer

**라이선스**: 명시되지 않음

**사용 용도**: 개인 사용 및 학습 목적

**면책 조항**:
- 이 소프트웨어는 YouTube 콘텐츠를 다운로드하는 도구입니다
- YouTube 서비스 약관을 준수할 책임은 사용자에게 있습니다
- 저작권이 있는 콘텐츠를 무단으로 다운로드하지 마십시오
- 개발자는 이 소프트웨어의 오용으로 인한 법적 책임을 지지 않습니다

**기여**: GitHub에서 이슈 및 풀 리퀘스트를 통해 기여 가능

**연락처**: GitHub Issues 페이지 이용
