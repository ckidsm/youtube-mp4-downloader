"""
FFmpeg와 AtomicParsley 의존성 확인 및 자동 설치
"""

import os
import sys
import subprocess
import platform
import urllib.request
import tarfile
import zipfile
import shutil
from pathlib import Path


class DependencyChecker:
    def __init__(self):
        self.system = platform.system()
        self.base_dir = self._get_base_dir()
        self.bin_dir = os.path.join(self.base_dir, 'bin')

        # bin 디렉토리 생성
        os.makedirs(self.bin_dir, exist_ok=True)

    def _get_base_dir(self):
        """앱 기본 디렉토리 가져오기"""
        if getattr(sys, 'frozen', False):
            # PyInstaller로 빌드된 경우
            if self.system == 'Darwin':
                # macOS .app 번들
                return os.path.dirname(sys.executable)
            else:
                return os.path.dirname(sys.executable)
        else:
            # 개발 모드
            return os.path.dirname(os.path.abspath(__file__))

    def _check_command(self, command):
        """명령어가 시스템에 설치되어 있는지 확인"""
        try:
            if self.system == 'Windows':
                subprocess.run(['where', command],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             check=True)
            else:
                subprocess.run(['which', command],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def _check_local_binary(self, name):
        """로컬 bin 디렉토리에 바이너리가 있는지 확인"""
        if self.system == 'Windows':
            binary_path = os.path.join(self.bin_dir, f'{name}.exe')
        else:
            binary_path = os.path.join(self.bin_dir, name)

        return os.path.exists(binary_path) and os.access(binary_path, os.X_OK)

    def _download_file(self, url, dest_path):
        """파일 다운로드"""
        print(f"다운로드 중: {url}")
        urllib.request.urlretrieve(url, dest_path)
        print(f"다운로드 완료: {dest_path}")

    def _install_ffmpeg_macos(self):
        """macOS용 FFmpeg 다운로드 및 설치"""
        print("FFmpeg를 다운로드하고 있습니다...")

        # FFmpeg static build 다운로드
        url = "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"
        zip_path = os.path.join(self.bin_dir, 'ffmpeg.zip')

        try:
            self._download_file(url, zip_path)

            # 압축 해제
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.bin_dir)

            # 실행 권한 부여
            ffmpeg_path = os.path.join(self.bin_dir, 'ffmpeg')
            os.chmod(ffmpeg_path, 0o755)

            # zip 파일 삭제
            os.remove(zip_path)

            print("FFmpeg 설치 완료!")
            return True
        except Exception as e:
            print(f"FFmpeg 설치 실패: {e}")
            return False

    def _install_atomicparsley_macos(self):
        """macOS용 AtomicParsley 다운로드 및 설치"""
        print("AtomicParsley를 다운로드하고 있습니다...")

        # GitHub에서 최신 릴리스 다운로드
        url = "https://github.com/wez/atomicparsley/releases/download/20240608.083822.1ed9031/AtomicParsleyMacOS.zip"
        zip_path = os.path.join(self.bin_dir, 'atomicparsley.zip')

        try:
            self._download_file(url, zip_path)

            # 압축 해제
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.bin_dir)

            # AtomicParsley 파일명 변경 (대소문자 통일)
            extracted_files = os.listdir(self.bin_dir)
            for file in extracted_files:
                if 'atomicparsley' in file.lower() and file != 'AtomicParsley':
                    old_path = os.path.join(self.bin_dir, file)
                    new_path = os.path.join(self.bin_dir, 'AtomicParsley')
                    if os.path.isfile(old_path):
                        shutil.move(old_path, new_path)
                        break

            # 실행 권한 부여
            atomicparsley_path = os.path.join(self.bin_dir, 'AtomicParsley')
            if os.path.exists(atomicparsley_path):
                os.chmod(atomicparsley_path, 0o755)

            # zip 파일 삭제
            os.remove(zip_path)

            print("AtomicParsley 설치 완료!")
            return True
        except Exception as e:
            print(f"AtomicParsley 설치 실패: {e}")
            return False

    def _install_ffmpeg_windows(self):
        """Windows용 FFmpeg 다운로드 및 설치"""
        print("FFmpeg를 다운로드하고 있습니다...")

        # FFmpeg Windows build
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = os.path.join(self.bin_dir, 'ffmpeg.zip')

        try:
            self._download_file(url, zip_path)

            # 압축 해제
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # ffmpeg.exe만 추출
                for file in zip_ref.namelist():
                    if file.endswith('bin/ffmpeg.exe'):
                        source = zip_ref.open(file)
                        target = open(os.path.join(self.bin_dir, 'ffmpeg.exe'), 'wb')
                        with source, target:
                            shutil.copyfileobj(source, target)
                        break

            os.remove(zip_path)
            print("FFmpeg 설치 완료!")
            return True
        except Exception as e:
            print(f"FFmpeg 설치 실패: {e}")
            return False

    def _install_atomicparsley_windows(self):
        """Windows용 AtomicParsley 다운로드 및 설치"""
        print("AtomicParsley를 다운로드하고 있습니다...")

        url = "https://github.com/wez/atomicparsley/releases/download/20240608.083822.1ed9031/AtomicParsleyWindows.zip"
        zip_path = os.path.join(self.bin_dir, 'atomicparsley.zip')

        try:
            self._download_file(url, zip_path)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.bin_dir)

            # 파일명 변경
            extracted_files = os.listdir(self.bin_dir)
            for file in extracted_files:
                if 'atomicparsley' in file.lower() and file.endswith('.exe'):
                    old_path = os.path.join(self.bin_dir, file)
                    new_path = os.path.join(self.bin_dir, 'AtomicParsley.exe')
                    if old_path != new_path:
                        shutil.move(old_path, new_path)
                    break

            os.remove(zip_path)
            print("AtomicParsley 설치 완료!")
            return True
        except Exception as e:
            print(f"AtomicParsley 설치 실패: {e}")
            return False

    def _install_ffmpeg_linux(self):
        """Linux용 FFmpeg 다운로드 및 설치"""
        print("FFmpeg를 다운로드하고 있습니다...")

        # FFmpeg static build
        url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        tar_path = os.path.join(self.bin_dir, 'ffmpeg.tar.xz')

        try:
            self._download_file(url, tar_path)

            # 압축 해제
            with tarfile.open(tar_path, 'r:xz') as tar_ref:
                for member in tar_ref.getmembers():
                    if member.name.endswith('/ffmpeg'):
                        member.name = 'ffmpeg'
                        tar_ref.extract(member, self.bin_dir)
                        break

            ffmpeg_path = os.path.join(self.bin_dir, 'ffmpeg')
            os.chmod(ffmpeg_path, 0o755)

            os.remove(tar_path)
            print("FFmpeg 설치 완료!")
            return True
        except Exception as e:
            print(f"FFmpeg 설치 실패: {e}")
            return False

    def _install_atomicparsley_linux(self):
        """Linux용 AtomicParsley 다운로드 및 설치"""
        print("AtomicParsley를 다운로드하고 있습니다...")

        url = "https://github.com/wez/atomicparsley/releases/download/20240608.083822.1ed9031/AtomicParsleyLinux.zip"
        zip_path = os.path.join(self.bin_dir, 'atomicparsley.zip')

        try:
            self._download_file(url, zip_path)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.bin_dir)

            # 파일명 변경
            extracted_files = os.listdir(self.bin_dir)
            for file in extracted_files:
                if 'atomicparsley' in file.lower() and file != 'AtomicParsley':
                    old_path = os.path.join(self.bin_dir, file)
                    new_path = os.path.join(self.bin_dir, 'AtomicParsley')
                    if os.path.isfile(old_path):
                        shutil.move(old_path, new_path)
                        break

            atomicparsley_path = os.path.join(self.bin_dir, 'AtomicParsley')
            if os.path.exists(atomicparsley_path):
                os.chmod(atomicparsley_path, 0o755)

            os.remove(zip_path)
            print("AtomicParsley 설치 완료!")
            return True
        except Exception as e:
            print(f"AtomicParsley 설치 실패: {e}")
            return False

    def check_and_install(self):
        """FFmpeg와 AtomicParsley 확인 및 설치"""
        print("\n의존성 확인 중...")

        # FFmpeg 확인
        ffmpeg_ok = False
        if self._check_local_binary('ffmpeg'):
            print("✓ FFmpeg (로컬): 설치됨")
            ffmpeg_ok = True
        elif self._check_command('ffmpeg'):
            print("✓ FFmpeg (시스템): 설치됨")
            ffmpeg_ok = True
        else:
            print("✗ FFmpeg: 설치되지 않음")
            print("FFmpeg 자동 설치를 시작합니다...")

            if self.system == 'Darwin':
                ffmpeg_ok = self._install_ffmpeg_macos()
            elif self.system == 'Windows':
                ffmpeg_ok = self._install_ffmpeg_windows()
            elif self.system == 'Linux':
                ffmpeg_ok = self._install_ffmpeg_linux()

        # AtomicParsley 확인
        atomicparsley_ok = False
        if self._check_local_binary('AtomicParsley'):
            print("✓ AtomicParsley (로컬): 설치됨")
            atomicparsley_ok = True
        elif self._check_command('AtomicParsley'):
            print("✓ AtomicParsley (시스템): 설치됨")
            atomicparsley_ok = True
        else:
            print("✗ AtomicParsley: 설치되지 않음")
            print("AtomicParsley 자동 설치를 시작합니다...")

            if self.system == 'Darwin':
                atomicparsley_ok = self._install_atomicparsley_macos()
            elif self.system == 'Windows':
                atomicparsley_ok = self._install_atomicparsley_windows()
            elif self.system == 'Linux':
                atomicparsley_ok = self._install_atomicparsley_linux()

        # PATH 환경변수에 bin 디렉토리 추가
        if ffmpeg_ok or atomicparsley_ok:
            current_path = os.environ.get('PATH', '')
            if self.bin_dir not in current_path:
                os.environ['PATH'] = f"{self.bin_dir}{os.pathsep}{current_path}"
                print(f"\nPATH에 {self.bin_dir} 추가됨")

        print("\n의존성 확인 완료!\n")

        return ffmpeg_ok and atomicparsley_ok


if __name__ == "__main__":
    checker = DependencyChecker()
    checker.check_and_install()
