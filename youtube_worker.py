"""
유튜브 다운로드를 위한 QThread 워커
"""

import os
import sys
import shutil
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal
import yt_dlp


def _remove_quarantine_macos(file_path):
    """macOS에서 파일의 quarantine 속성 제거"""
    import subprocess
    import platform

    if platform.system() == 'Darwin' and os.path.exists(file_path):
        try:
            subprocess.run(['xattr', '-d', 'com.apple.quarantine', file_path],
                         stderr=subprocess.DEVNULL, timeout=2)
            subprocess.run(['xattr', '-d', 'com.apple.provenance', file_path],
                         stderr=subprocess.DEVNULL, timeout=2)
        except Exception:
            pass


def _find_ffmpeg_path():
    """FFmpeg 경로 찾기 (시스템 또는 로컬 bin 디렉토리)"""
    # 1. 로컬 bin 디렉토리 확인 (PyInstaller 앱 번들 내부)
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 경우
        base_dir = os.path.dirname(sys.executable)
        local_ffmpeg = os.path.join(base_dir, 'bin', 'ffmpeg')
        if os.path.exists(local_ffmpeg) and os.access(local_ffmpeg, os.X_OK):
            # macOS에서 quarantine 속성 제거 시도
            _remove_quarantine_macos(local_ffmpeg)

            # AtomicParsley도 같은 디렉토리에 있을 수 있으므로 처리
            atomicparsley_path = os.path.join(base_dir, 'bin', 'AtomicParsley')
            if os.path.exists(atomicparsley_path):
                _remove_quarantine_macos(atomicparsley_path)

            return local_ffmpeg

    # 2. 시스템 PATH에서 확인
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path

    # 3. macOS Homebrew 기본 경로 확인
    homebrew_paths = [
        '/opt/homebrew/bin/ffmpeg',  # Apple Silicon
        '/usr/local/bin/ffmpeg'       # Intel Mac
    ]
    for path in homebrew_paths:
        if os.path.exists(path):
            return path

    return None


class YoutubeDownloadWorker(QThread):
    """백그라운드에서 유튜브 다운로드를 처리하는 워커"""

    # 시그널 정의
    progress = pyqtSignal(str)  # 진행 상태 텍스트
    title_resolved = pyqtSignal(str)  # 영상 제목 확인됨
    file_path_resolved = pyqtSignal(str)  # 실제 다운로드된 파일 경로
    finished = pyqtSignal(bool, str)  # (성공여부, 메시지)

    def __init__(self, url: str, output_path: str, download_type: str = 'audio'):
        """
        Args:
            url: 유튜브 URL
            output_path: 저장 경로
            download_type: 'audio' (M4A), 'video_best' (최고화질 비디오), 'video_720p', 'video_480p'
        """
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.download_type = download_type
        self._is_cancelled = False

    def cancel(self):
        """다운로드 취소"""
        self._is_cancelled = True

    def run(self):
        """다운로드 실행"""
        try:
            # 저장 폴더 생성
            Path(self.output_path).parent.mkdir(parents=True, exist_ok=True)

            # 파일명에서 확장자 제거 (yt-dlp가 자동으로 추가)
            base_path = os.path.splitext(self.output_path)[0]

            # FFmpeg 경로 찾기
            ffmpeg_location = _find_ffmpeg_path()
            if not ffmpeg_location:
                self.finished.emit(False, "FFmpeg를 찾을 수 없습니다. FFmpeg를 설치해주세요.")
                return

            # 다운로드 타입에 따른 옵션 설정
            if self.download_type == 'audio':
                ydl_opts = {
                    # 최고 음질 오디오 선택 (유튜브의 경우 일반적으로 Opus ~160kbps 또는 AAC ~256kbps)
                    'format': 'bestaudio/best',
                    'outtmpl': base_path + '.%(ext)s',
                    'noplaylist': True,  # 플레이리스트 무시, 단일 비디오만
                    'writethumbnail': True,  # 썸네일 다운로드
                    'ffmpeg_location': ffmpeg_location,  # FFmpeg 경로 명시
                    'postprocessors': [
                        {
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'm4a',
                            'preferredquality': '320',  # 320kbps로 변환 (원본이 더 낮으면 원본 유지)
                        },
                        {
                            'key': 'EmbedThumbnail',  # 썸네일을 앨범 아트로 임베드
                        },
                    ],
                    # 추가 오디오 품질 옵션
                    'postprocessor_args': [
                        '-ar', '48000',  # 샘플링 레이트 48kHz (고음질)
                    ],
                    'prefer_ffmpeg': True,
                    'keepvideo': False,
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [self._progress_hook],
                }
            elif self.download_type == 'video_best':
                ydl_opts = {
                    # 최고 화질 비디오 + 최고 음질 오디오
                    'format': 'bestvideo[ext=mp4]+bestaudio/best[ext=mp4]/best',
                    'outtmpl': base_path + '.%(ext)s',
                    'noplaylist': True,  # 플레이리스트 무시
                    'writethumbnail': True,  # 썸네일 다운로드
                    'ffmpeg_location': ffmpeg_location,  # FFmpeg 경로 명시
                    'merge_output_format': 'mp4',
                    'postprocessors': [
                        {
                            'key': 'EmbedThumbnail',  # 썸네일을 비디오에 임베드
                        },
                    ],
                    'postprocessor_args': [
                        '-c:a', 'aac',  # AAC 오디오 코덱
                        '-b:a', '320k',  # 오디오 비트레이트 320kbps
                        '-ar', '48000',  # 샘플링 레이트 48kHz
                    ],
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [self._progress_hook],
                }
            elif self.download_type == 'video_720p':
                ydl_opts = {
                    # 720p 비디오 + 최고 음질 오디오
                    'format': 'bestvideo[height<=720][ext=mp4]+bestaudio/best[height<=720][ext=mp4]/best',
                    'outtmpl': base_path + '.%(ext)s',
                    'noplaylist': True,  # 플레이리스트 무시
                    'writethumbnail': True,  # 썸네일 다운로드
                    'ffmpeg_location': ffmpeg_location,  # FFmpeg 경로 명시
                    'merge_output_format': 'mp4',
                    'postprocessors': [
                        {
                            'key': 'EmbedThumbnail',  # 썸네일을 비디오에 임베드
                        },
                    ],
                    'postprocessor_args': [
                        '-c:a', 'aac',
                        '-b:a', '256k',  # 720p는 256kbps
                        '-ar', '48000',
                    ],
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [self._progress_hook],
                }
            elif self.download_type == 'video_480p':
                ydl_opts = {
                    # 480p 비디오 + 고음질 오디오
                    'format': 'bestvideo[height<=480][ext=mp4]+bestaudio/best[height<=480][ext=mp4]/best',
                    'outtmpl': base_path + '.%(ext)s',
                    'noplaylist': True,  # 플레이리스트 무시
                    'writethumbnail': True,  # 썸네일 다운로드
                    'ffmpeg_location': ffmpeg_location,  # FFmpeg 경로 명시
                    'merge_output_format': 'mp4',
                    'postprocessors': [
                        {
                            'key': 'EmbedThumbnail',  # 썸네일을 비디오에 임베드
                        },
                    ],
                    'postprocessor_args': [
                        '-c:a', 'aac',
                        '-b:a', '192k',  # 480p는 192kbps
                        '-ar', '48000',
                    ],
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [self._progress_hook],
                }
            else:
                ydl_opts = {
                    'format': 'best[ext=mp4]/best',
                    'outtmpl': base_path + '.%(ext)s',
                    'ffmpeg_location': ffmpeg_location,  # FFmpeg 경로 명시
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [self._progress_hook],
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 취소 확인
                if self._is_cancelled:
                    self.finished.emit(False, "취소됨")
                    return

                # 영상 정보 가져오기
                self.progress.emit("정보 수집 중...")
                info = ydl.extract_info(self.url, download=False)
                video_title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)

                # 제목 시그널 발생
                self.title_resolved.emit(video_title)

                # 취소 확인
                if self._is_cancelled:
                    self.finished.emit(False, "취소됨")
                    return

                # 다운로드 시작
                self.progress.emit(f"다운로드 시작... ({duration // 60}분 {duration % 60}초)")

                # 다운로드 실행 및 결과 받기
                result = ydl.extract_info(self.url, download=True)

                # 취소 확인
                if self._is_cancelled:
                    self.finished.emit(False, "취소됨")
                    return

                # 실제 다운로드된 파일 경로 찾기
                downloaded_file = ydl.prepare_filename(result)

                # 오디오 전용인 경우 확장자가 변경됨
                if self.download_type == 'audio':
                    # m4a 확장자로 변경
                    downloaded_file = os.path.splitext(downloaded_file)[0] + '.m4a'

                # 실제 파일이 존재하는지 확인하고 경로 전송
                if os.path.exists(downloaded_file):
                    self.file_path_resolved.emit(downloaded_file)
                else:
                    # 파일을 찾을 수 없으면 디렉토리에서 검색
                    base_dir = os.path.dirname(downloaded_file)
                    base_name = os.path.splitext(os.path.basename(downloaded_file))[0]
                    ext = '.m4a' if self.download_type == 'audio' else '.mp4'

                    # 디렉토리에서 유사한 파일 찾기
                    if os.path.exists(base_dir):
                        for file in os.listdir(base_dir):
                            if file.endswith(ext) and base_name[:30] in file:
                                downloaded_file = os.path.join(base_dir, file)
                                self.file_path_resolved.emit(downloaded_file)
                                break

                self.progress.emit("완료!")
                self.finished.emit(True, f"다운로드 완료: {video_title}")

        except Exception as e:
            self.progress.emit(f"오류: {str(e)}")
            self.finished.emit(False, f"오류: {str(e)}")

    def _progress_hook(self, d):
        """yt-dlp 진행 상태 후크"""
        if self._is_cancelled:
            raise Exception("Download cancelled by user")

        if d['status'] == 'downloading':
            # 다운로드 중
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            self.progress.emit(f"다운로드 중: {percent} (속도: {speed}, ETA: {eta})")
        elif d['status'] == 'finished':
            # 다운로드 완료, 후처리 중
            self.progress.emit("후처리 중...")
