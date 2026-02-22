# YouTube High-Quality Downloader

Cross-platform YouTube video/audio downloader with PyQt6 GUI

---

## 1. Overview

YouTube High-Quality Downloader is a desktop application that downloads high-quality audio (M4A 320kbps) or video (MP4) from YouTube videos.

This system is designed for individual users who want to save YouTube content locally and play it offline. It targets users who want to enjoy music lectures, podcasts, educational materials, and more without an internet connection.

Through the PyQt6 GUI, users can add multiple videos to a queue and download them simultaneously. The application automatically embeds YouTube thumbnails as album art, providing an enhanced visual experience in music players.

The system automatically downloads and installs FFmpeg and AtomicParsley, so users can run the program immediately without any additional setup. It supports macOS, Windows, and Linux, providing optimized executables for each platform.

---

## 2. Key Features

1. **High-Quality Audio Download** - M4A format at 320kbps, 48kHz sampling (`youtube_worker.py`)
2. **Multi-Quality Video Download** - MP4 best quality, 720p, 480p selectable (`youtube_worker.py`)
3. **Automatic Thumbnail Album Art Embedding** - YouTube thumbnails embedded as metadata (`youtube_worker.py`)
4. **Automatic Dependency Installation** - FFmpeg/AtomicParsley auto-download and setup (`dependency_checker.py`)
5. **Download Queue Management** - Multiple simultaneous downloads with progress tracking (`youtube_ui.py`)
6. **Automatic Title Extraction** - Auto-fetch video titles from URLs with safe filename conversion (`youtube_ui.py`)
7. **Settings Persistence** - Automatic save and restore of download paths (`youtube_ui.py`, `settings.json`)
8. **Cross-Platform Build** - macOS, Windows, Linux executable generation (`build_*.sh/.bat`)
9. **Real-Time Progress Display** - Live download speed, ETA, and progress updates (`youtube_worker.py`)
10. **Integrated Player** - Double-click to instantly play completed files (`youtube_ui.py`)

---

## 3. Concepts / Domain Model

### Download Queue
- List of download tasks added by the user
- Location: `youtube_ui.py` (QTableWidget)
- Each item includes URL, save path, filename, format, quality, progress status

### Download Worker
- QThread-based background download execution unit
- Location: `youtube_worker.py` (YoutubeDownloadWorker class)
- Provides async download, progress signals, cancellation functionality

### Download Type
- Media format and quality to download
- Location: `youtube_worker.py` (ydl_opts configuration)
- Types: audio (M4A 320kbps), video_best, video_720p, video_480p

### Dependency
- Required external binaries (FFmpeg, AtomicParsley)
- Location: `dependency_checker.py` (DependencyChecker class)
- System installation check → Auto-download if missing → Save to local bin folder

### Settings
- User environment settings (download path)
- Location: `youtube_ui.py` (_load_settings, _save_settings methods)
- Save location: `settings.json` (app execution directory)

### File Path Tracking
- Mapping between actual downloaded file paths and queue rows
- Location: `youtube_ui.py` (self.file_paths dictionary)
- Links actual filenames created by yt-dlp with UI display

---

## 4. Architecture

### Components

**Desktop Application Layer**
- PyQt6-based GUI application (`youtube_ui.py`)
- Receives user input, manages download queue, displays progress
- Manages download list with QTableWidget, provides context menu

**Worker Layer**
- QThread-based async download workers (`youtube_worker.py`)
- Executes YouTube video downloads via yt-dlp
- Communicates with UI via progress, title_resolved, file_path_resolved, finished signals

**Dependency Management Layer**
- Automatic dependency installation system (`dependency_checker.py`)
- Checks system environment, downloads platform-specific binaries, sets PATH

**External Tools**
- FFmpeg: Audio/video conversion and post-processing
- AtomicParsley: M4A metadata and album art embedding
- yt-dlp: YouTube video download engine

### Data Flow

1. **User Input**: Enter URL → Auto-fetch title → Add to queue
2. **Start Download**: Select items in UI → Create and start Worker
3. **Download Progress**: Worker executes yt-dlp → Emits progress signals → UI updates
4. **Post-Processing**: FFmpeg converts audio → AtomicParsley embeds thumbnail
5. **Completion**: Send actual file path → Display completion in UI → Save file path

### Authentication/Authorization Flow

No authentication system (local desktop application)

### Settings Persistence Flow

1. **Load**: App starts → Read settings.json → Restore save path
2. **Save**: User selects folder → Record path in settings.json

---

## 5. Source Structure

```
youtubuDn/
├── youtube_ui.py              # Main GUI application (entry point)
│                              # - PyQt6-based window and widget composition
│                              # - Download queue management (QTableWidget)
│                              # - Worker creation and signal connection
│                              # - Context menu, file playback, settings management
│
├── youtube_worker.py          # QThread download worker
│                              # - yt-dlp execution and progress tracking
│                              # - Platform-specific download options
│                              # - Thumbnail embedding configuration
│                              # - Cancellation and timeout handling
│
├── dependency_checker.py      # Automatic dependency installation module
│                              # - FFmpeg/AtomicParsley installation check
│                              # - Platform-specific binary download
│                              # - Local bin folder management
│                              # - PATH environment variable setup
│
├── youtube_downloader.py      # CLI version downloader
│                              # - Command-line argument parsing
│                              # - Simple download execution
│
├── youtube_downloader.spec    # PyInstaller build configuration (macOS)
│                              # - Specify dependencies and data files
│                              # - .app bundle configuration
│
├── build_macos.sh             # macOS build script
├── build_windows.bat          # Windows build script
├── build_linux.sh             # Linux build script
│
├── requirements.txt           # Python package dependencies
│                              # - yt-dlp, PyQt6, pyinstaller
│
├── run_gui.sh                 # Development environment GUI execution script
├── README.md                  # Project introduction and usage
├── INSTALL.md                 # Detailed installation guide
└── .gitignore                 # Git exclusion file list
```

### Main Entry Points

- **GUI Version**: `youtube_ui.py` → `main()` → `YoutubeDownloaderApp` class
- **CLI Version**: `youtube_downloader.py` → `main()` → `download_youtube_audio()`

### Build Output

- macOS: `dist/YoutubeDownloader.app`
- Windows: `dist/YoutubeDownloader.exe`
- Linux: `dist/YoutubeDownloader`

---

## 6. How It Works

### Application Startup

1. Execute `youtube_ui.py` → Call `main()` function
2. Create `DependencyChecker` instance → Execute `check_and_install()`
   - Check FFmpeg installation → Auto-download if missing
   - Check AtomicParsley installation → Auto-download if missing
   - Save to local `bin/` folder → Add to PATH
3. Create `QApplication` and `YoutubeDownloaderApp` window
4. Load save path from `settings.json` → Display in UI

### Download Request Flow

1. **Enter URL and Fetch Title**
   - User enters URL → Click "Fetch Title" button (optional)
   - `fetch_video_title()`: Extract video info with yt-dlp → Display title
   - Clean URL: Remove playlist parameters (`_clean_url()`)

2. **Add to Queue**
   - Click "Add to Queue" → Execute `add_to_queue()`
   - Auto-fetch title if filename is empty
   - Sanitize filename: Remove emojis, special characters (`_sanitize_filename()`)
   - Add new row to QTableWidget (URL, path, filename, format, quality, status)

3. **Start Download**
   - User selects row → Click "Download Selected"
   - `start_selected()`: Create `YoutubeDownloadWorker` for each selected row
   - Connect worker signals:
     - `progress` → Update UI progress status
     - `title_resolved` → Update filename with video title
     - `file_path_resolved` → Save actual download file path
     - `finished` → Handle completion/failure
   - Start worker thread (`worker.start()`)

4. **Execute Download (Worker Thread)**
   - `youtube_worker.py`: Execute `run()` method
   - Configure yt-dlp options (format, quality, thumbnail embedding)
   - Extract video info → Emit `title_resolved` signal
   - Execute download → Progress callback → Emit `progress` signal
   - FFmpeg post-processing: Audio conversion, sampling rate setup
   - AtomicParsley: Embed thumbnail as album art
   - Verify actual file path → Emit `file_path_resolved` signal
   - Emit `finished` signal (success/failure)

5. **Completion Handling**
   - Call `_on_finished()` in UI
   - Update progress status to "✓ Complete" or "✗ Failed"
   - Clean up worker (`worker.deleteLater()`)

### File Playback

1. User double-clicks completed row → Call `_on_double_click()`
2. Check actual file path in `file_paths` dictionary
3. Open file with platform-specific default player
   - macOS: `open` command
   - Windows: `os.startfile()`
   - Linux: `xdg-open` command

### Cancellation and Removal

1. User clicks "Stop Selected" → Execute `stop_selected()`
2. Call worker's `cancel()` method → Set `_is_cancelled` flag
3. Wait for 2-second timeout → Force terminate with `terminate()` if not stopped
4. Clean up worker and update UI status

---

## 7. Setup & Run

### Prerequisites

- **Python**: 3.8 or higher (Development: Python 3.13)
- **Virtual Environment**: venv recommended
- **FFmpeg & AtomicParsley**: Auto-installed (optional manual install)

### Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

### Development Mode Execution

**GUI Version:**
```bash
python youtube_ui.py
```

Or:
```bash
chmod +x run_gui.sh
./run_gui.sh
```

**CLI Version:**
```bash
# Interactive mode
python youtube_downloader.py

# Command-line arguments
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
python youtube_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" "downloads"
```

### Production Build

**macOS:**
```bash
chmod +x build_macos.sh
./build_macos.sh
# Output: dist/YoutubeDownloader.app
```

**Windows:**
```cmd
build_windows.bat
REM Output: dist\YoutubeDownloader.exe
```

**Linux:**
```bash
chmod +x build_linux.sh
./build_linux.sh
# Output: dist/YoutubeDownloader
```

### Environment Variables

No environment variables (all settings stored in `settings.json`)

### Configuration File

**settings.json** (auto-generated in app execution directory)
```json
{
  "download_path": "/Users/username/Downloads"
}
```

---

## 8. Server Requirements / Spec

This project is a **local desktop application** with no server requirements.

### Client Requirements

**Required Ports**: None (local execution)

**Memory Requirements**:
- Minimum: 512MB (Python + PyQt6)
- Recommended: 1GB or more (for multiple downloads)

**CPU Requirements**:
- Minimum: 1 core (single download)
- Recommended: 2 cores or more (multiple downloads)

**Storage Requirements**:
- App size: ~50MB (built executable)
- Download space: Depends on user's downloaded file sizes
- Logs: None (console output only)

**Network Requirements**:
- Internet connection required (YouTube download and automatic dependency installation)

---

## 9. Operations

### Logging

**Location**: Standard output (console)
**Level**: Informational messages via `print()` statements
**Content**:
- Dependency check results
- Download progress status
- Error messages

In development mode, outputs to terminal; in built app, outputs to system log or ignored.

### Health Check

No health check endpoint (desktop application)

### Backup and Migration

**Backup Targets**:
- `settings.json`: User save path settings
- Downloaded files: User-specified folder

**Migration**: None (no database)

### Deployment Method

**Build Tool**: PyInstaller
- `youtube_downloader.spec` (macOS)
- `build_macos.sh`, `build_windows.bat`, `build_linux.sh`

**Deployment Process**:
1. Run build script on each platform
2. Distribute executable from `dist/` folder
3. Users simply download and run

**Updates**:
- Manual update (download and replace new version)
- No automatic update feature

---

## 10. Security Notes

### Authentication/Session

No authentication system (local application)

### Permissions

**File System Permissions**:
- Write permission required for user-selected folder
- macOS: May request "Folder Access" permission on first run

**Network Permissions**:
- YouTube server access
- Dependency download server access (evermeet.cx, gyan.dev, johnvansickle.com, GitHub)

### Input Validation

**URL Validation**:
- `_clean_url()`: URL parsing and unnecessary parameter removal (`youtube_ui.py:190-221`)
- yt-dlp rejects invalid URLs

**Filename Validation**:
- `_sanitize_filename()`: Remove special characters, emojis, path separators (`youtube_ui.py:321-354`)
- Filename length limit (200 characters)

### Sensitive Information/Secrets Handling

No sensitive information

**Stored Information**:
- `settings.json`: Contains only save path (plain text)
- Downloaded files: User-selected folder

### Code Signing

**macOS**: `codesign_identity=None` in `youtube_downloader.spec` (unsigned)
**Windows**: Unsigned
**Linux**: Unsigned

Users may need to manually approve "Unidentified Developer" warnings.

---

## 11. Troubleshooting

### macOS: "Unidentified Developer" Warning

**Issue**: Security warning when running app
**Solution**:
```bash
xattr -cr /path/to/YoutubeDownloader.app
```
Or System Settings > Privacy & Security > Security > "Open Anyway"

### Windows: "Windows Defender" Warning

**Issue**: SmartScreen warning
**Solution**: Click "More info" → "Run anyway"

### Album Art Not Displaying

**Issue**: AtomicParsley not installed
**Check**:
```bash
# macOS/Linux
which AtomicParsley

# Windows
where AtomicParsley
```
**Solution**: Restart program (auto-download) or manual install

### Download Stuck

**Issue**: Network timeout or YouTube restrictions
**Solution**:
1. Click "Stop Selected"
2. Remove item and retry
3. Verify URL (single video, not playlist)

### File Not Found (When Double-Clicking)

**Issue**: Download path changed or file deleted
**Solution**:
1. Context menu → "Open Download Folder"
2. Manually check file
3. Re-download if file missing

### Python Version Error

**Issue**: Using Python 3.7 or lower
**Solution**: Install Python 3.8 or higher
```bash
python3 --version
```

---

## 12. License / Disclaimer

**License**: Not specified

**Usage Purpose**: Personal use and educational purposes only

**Disclaimer**:
- This software is a tool for downloading YouTube content
- Users are responsible for complying with YouTube's Terms of Service
- Do not download copyrighted content without permission
- The developer is not liable for legal issues arising from misuse of this software

**Contributing**: Contributions welcome via GitHub Issues and Pull Requests

**Contact**: Use GitHub Issues page

---

## Quick Start

```bash
# Clone repository
git clone https://github.com/ckidsm/youtube-mp4-downloader.git
cd youtube-mp4-downloader

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run GUI
python youtube_ui.py

# Build (macOS example)
./build_macos.sh
```

---

## Screenshots

GUI application with download queue management, real-time progress display, and integrated file player.

---

## Credits

Built with:
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube download engine
- [FFmpeg](https://ffmpeg.org/) - Audio/video processing
- [AtomicParsley](https://github.com/wez/atomicparsley) - Metadata handling
- [PyInstaller](https://www.pyinstaller.org/) - Executable builder
