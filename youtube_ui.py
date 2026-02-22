"""
유튜브 다운로더 PyQt6 UI
"""

import os
import re
import sys
import subprocess
import json
from typing import Dict, Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,
    QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QComboBox, QGroupBox, QAbstractItemView, QMenu
)
from PyQt6.QtGui import QAction
import yt_dlp

from youtube_worker import YoutubeDownloadWorker
from dependency_checker import DependencyChecker

# 설정 파일 경로
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")


class YoutubeDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("유튜브 고음질 다운로더 (PyQt6)")
        self.resize(1000, 600)

        # 메인 레이아웃
        main_layout = QVBoxLayout(self)

        # ── 입력 섹션 ──
        input_group = QGroupBox("다운로드 설정")
        input_layout = QVBoxLayout()

        # URL 입력
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("유튜브 URL:"))
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://www.youtube.com/watch?v=...")
        url_layout.addWidget(self.url_edit, 1)

        btn_fetch_title = QPushButton("제목 가져오기")
        btn_fetch_title.clicked.connect(self.fetch_video_title)
        url_layout.addWidget(btn_fetch_title)

        input_layout.addLayout(url_layout)

        # 저장 경로 및 파일명
        save_layout = QHBoxLayout()
        save_layout.addWidget(QLabel("저장 경로:"))
        self.dir_edit = QLineEdit("downloads")
        self.dir_edit.setPlaceholderText("downloads")
        save_layout.addWidget(self.dir_edit, 1)

        btn_dir = QPushButton("폴더 선택...")
        btn_dir.clicked.connect(self.choose_dir)
        save_layout.addWidget(btn_dir)

        save_layout.addWidget(QLabel("파일명:"))
        self.filename_edit = QLineEdit()
        self.filename_edit.setPlaceholderText("자동 (영상 제목)")
        save_layout.addWidget(self.filename_edit)
        input_layout.addLayout(save_layout)

        # 다운로드 타입 선택
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("다운로드 형식:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "오디오 전용 (M4A - 최고 음질)",
            "비디오 (MP4 - 최고 화질)",
            "비디오 (MP4 - 720p)",
            "비디오 (MP4 - 480p)"
        ])
        self.type_combo.setCurrentIndex(0)
        type_layout.addWidget(self.type_combo, 1)
        type_layout.addStretch()
        input_layout.addLayout(type_layout)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # ── 버튼 섹션 ──
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("큐에 추가")
        self.btn_add.clicked.connect(self.add_to_queue)

        self.btn_start = QPushButton("선택 항목 다운로드")
        self.btn_start.clicked.connect(self.start_selected)

        self.btn_stop = QPushButton("선택 항목 중지")
        self.btn_stop.clicked.connect(self.stop_selected)

        self.btn_remove = QPushButton("선택 항목 제거")
        self.btn_remove.clicked.connect(self.remove_selected)

        self.btn_clear = QPushButton("완료 항목 정리")
        self.btn_clear.clicked.connect(self.clear_completed)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # ── 다운로드 큐 테이블 ──
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "URL", "저장 경로", "파일명", "형식", "음질", "진행 상태"
        ])

        # 테이블 설정
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # 읽기 전용
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)  # Row 전체 선택
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)  # 다중 선택 가능
        self.table.cellDoubleClicked.connect(self._on_double_click)  # 더블클릭 이벤트
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)  # 컨텍스트 메뉴 활성화
        self.table.customContextMenuRequested.connect(self._show_context_menu)  # 컨텍스트 메뉴 이벤트

        # 컬럼 크기 설정
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        self.table.setColumnWidth(0, 320)  # URL
        self.table.setColumnWidth(1, 100)  # 저장 경로
        self.table.setColumnWidth(2, 180)  # 파일명
        self.table.setColumnWidth(3, 120)  # 형식
        self.table.setColumnWidth(4, 100)  # 음질

        main_layout.addWidget(self.table)

        # 워커 관리
        self.workers: Dict[int, YoutubeDownloadWorker] = {}

        # 파일 경로 추적 (row -> 실제 파일 경로)
        self.file_paths: Dict[int, str] = {}

        # 저장된 경로 로드
        saved_path = self._load_settings()
        if saved_path:
            self.dir_edit.setText(saved_path)

    def _load_settings(self) -> Optional[str]:
        """설정 파일에서 저장 경로 로드"""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return settings.get('download_path', None)
        except Exception as e:
            print(f"설정 로드 실패: {e}")
        return None

    def _save_settings(self, download_path: str):
        """설정 파일에 저장 경로 저장"""
        try:
            settings = {'download_path': download_path}
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"설정 저장 실패: {e}")

    def choose_dir(self):
        """저장 경로 선택 다이얼로그"""
        d = QFileDialog.getExistingDirectory(self, "저장 경로 선택")
        if d:
            self.dir_edit.setText(d)
            self._save_settings(d)  # 저장 경로를 설정 파일에 저장

    def fetch_video_title(self):
        """유튜브 URL에서 영상 제목 가져오기"""
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "입력 오류", "유튜브 URL을 입력해주세요.")
            return

        # 플레이리스트 파라미터 제거 (단일 비디오만 처리)
        url = self._clean_url(url)

        try:
            # yt-dlp로 영상 정보 가져오기
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'noplaylist': True,  # 플레이리스트 무시, 단일 비디오만
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)

                # 제목을 안전한 파일명으로 변환
                safe_title = self._sanitize_filename(video_title)[:60]

                # 파일명 입력창에 설정
                self.filename_edit.setText(safe_title)

                # 정보 표시
                QMessageBox.information(
                    self,
                    "영상 정보",
                    f"제목: {video_title}\n길이: {duration // 60}분 {duration % 60}초\n\n파일명이 자동으로 설정되었습니다."
                )

        except Exception as e:
            QMessageBox.warning(self, "오류", f"영상 정보를 가져올 수 없습니다:\n{str(e)}")

    def _clean_url(self, url: str) -> str:
        """URL에서 불필요한 파라미터 제거"""
        import urllib.parse

        # URL 파싱
        parsed = urllib.parse.urlparse(url)

        # 쿼리 파라미터 파싱
        query_params = urllib.parse.parse_qs(parsed.query)

        # 불필요한 파라미터 제거
        # list, index: 플레이리스트 관련
        # start_radio: 자동재생 관련
        # si: 공유 식별자
        # feature: 특정 기능 식별자
        cleaned_params = {k: v for k, v in query_params.items()
                         if k not in ['list', 'index', 'start_radio', 'si', 'feature']}

        # 정리된 쿼리 문자열 생성
        cleaned_query = urllib.parse.urlencode(cleaned_params, doseq=True)

        # URL 재구성
        cleaned_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            cleaned_query,
            parsed.fragment
        ))

        return cleaned_url

    def _show_context_menu(self, position):
        """마우스 오른쪽 클릭 컨텍스트 메뉴"""
        # 선택된 행이 있는지 확인
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()))
        if not selected_rows:
            return

        # 컨텍스트 메뉴 생성
        menu = QMenu(self)

        # 다운로드 폴더 열기 액션
        open_folder_action = QAction("다운로드 폴더 열기", self)
        open_folder_action.triggered.connect(lambda: self._open_download_folder(selected_rows[0]))
        menu.addAction(open_folder_action)

        # 파일 재생 액션 (완료된 경우만)
        if selected_rows:
            row = selected_rows[0]
            status = self.table.item(row, 5).text()  # 진행 상태는 5번 컬럼
            if "완료" in status:
                play_action = QAction("파일 재생", self)
                play_action.triggered.connect(lambda: self._play_file(row))
                menu.addAction(play_action)

        # 메뉴 표시
        menu.exec(self.table.viewport().mapToGlobal(position))

    def _open_download_folder(self, row: int):
        """다운로드 폴더 열기"""
        if row < self.table.rowCount():
            save_dir = self.table.item(row, 1).text()

            # 폴더가 없으면 생성
            if not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)

            # 운영체제에 맞게 폴더 열기
            try:
                if sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', save_dir])
                elif sys.platform == 'win32':  # Windows
                    os.startfile(save_dir)
                else:  # Linux
                    subprocess.run(['xdg-open', save_dir])
            except Exception as e:
                QMessageBox.warning(self, "오류", f"폴더를 열 수 없습니다:\n{str(e)}")

    def _play_file(self, row: int):
        """파일 재생"""
        if row in self.file_paths:
            file_path = self.file_paths[row]
        else:
            save_dir = self.table.item(row, 1).text()
            filename = self.table.item(row, 2).text()
            file_path = os.path.join(save_dir, filename)

        # 파일 존재 확인
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "파일 없음", f"파일을 찾을 수 없습니다:\n{file_path}")
            return

        # 운영체제에 맞게 기본 플레이어로 재생
        try:
            if sys.platform == 'darwin':  # macOS
                subprocess.run(['open', file_path])
            elif sys.platform == 'win32':  # Windows
                os.startfile(file_path)
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            QMessageBox.warning(self, "재생 오류", f"파일 재생 중 오류가 발생했습니다:\n{str(e)}")

    def _get_download_type_key(self, index: int) -> str:
        """콤보박스 인덱스를 다운로드 타입 키로 변환"""
        types = {
            0: 'audio',
            1: 'video_best',
            2: 'video_720p',
            3: 'video_480p'
        }
        return types.get(index, 'audio')

    def _get_extension(self, download_type: str) -> str:
        """다운로드 타입에 따른 확장자 반환"""
        if download_type == 'audio':
            return '.m4a'
        return '.mp4'

    def _get_quality_info(self, download_type: str) -> str:
        """다운로드 타입에 따른 음질 정보 반환"""
        quality_map = {
            'audio': '320kbps M4A',
            'video_best': '320kbps AAC',
            'video_720p': '256kbps AAC',
            'video_480p': '192kbps AAC'
        }
        return quality_map.get(download_type, 'N/A')

    def _sanitize_filename(self, name: str) -> str:
        """파일명을 안전하게 정제"""
        name = (name or "download").strip()

        # 이모지 및 비ASCII 특수문자 제거 (한글, 일본어, 중국어는 유지)
        # Unicode 범위: 이모지 제거, 한중일 문자 유지
        import unicodedata
        cleaned_name = ""
        for char in name:
            # 이모지 및 기타 심볼 제거
            if unicodedata.category(char).startswith('So'):  # Symbol, Other
                continue
            # 이모지 modifier 제거
            if '\U0001F000' <= char <= '\U0001FFFF':  # Emoji 범위
                continue
            cleaned_name += char

        name = cleaned_name.strip()

        # 경로 구분자 및 상위 디렉토리 참조 제거
        name = name.replace(os.sep, "_").replace("/", "_").replace("\\", "_")
        name = re.sub(r'\.\.+', '_', name)

        # 파일명에 허용되지 않는 문자 제거 (Windows 호환)
        name = re.sub(r'[<>:"|?*]', '_', name)

        # 연속된 공백을 하나로
        name = re.sub(r'\s+', ' ', name)

        # 파일명 길이 제한 (너무 긴 경우 잘라냄)
        if len(name) > 200:
            name = name[:200]

        return name.strip() or "download"

    def add_to_queue(self):
        """다운로드 큐에 항목 추가"""
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "입력 오류", "유튜브 URL을 입력해주세요.")
            return

        # URL 정리
        url = self._clean_url(url)

        save_dir = self.dir_edit.text().strip() or "downloads"
        filename = self.filename_edit.text().strip()
        download_type_idx = self.type_combo.currentIndex()
        download_type = self._get_download_type_key(download_type_idx)

        # 파일명이 없으면 자동으로 영상 제목 가져오기 시도
        if not filename:
            try:
                # 간단하게 제목만 가져오기
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'noplaylist': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_title = info.get('title', 'download')
                    filename = self._sanitize_filename(video_title)[:60]
            except:
                # 제목 가져오기 실패 시 기본값 사용
                filename = "download"
        else:
            filename = self._sanitize_filename(filename)

        # 확장자 추가
        ext = self._get_extension(download_type)
        if not filename.endswith(ext):
            filename = os.path.splitext(filename)[0] + ext

        # 테이블에 행 추가
        row = self.table.rowCount()
        self.table.insertRow(row)

        # 음질 정보 가져오기
        quality_info = self._get_quality_info(download_type)

        # 데이터 입력
        self.table.setItem(row, 0, QTableWidgetItem(url))
        self.table.setItem(row, 1, QTableWidgetItem(save_dir))
        self.table.setItem(row, 2, QTableWidgetItem(filename))
        self.table.setItem(row, 3, QTableWidgetItem(self.type_combo.currentText()))
        self.table.setItem(row, 4, QTableWidgetItem(quality_info))
        self.table.setItem(row, 5, QTableWidgetItem("대기 중"))

        # 파일 경로 저장
        self.file_paths[row] = os.path.join(save_dir, filename)

        # 입력 필드 초기화
        self.url_edit.clear()
        self.filename_edit.clear()

        QMessageBox.information(self, "추가 완료", "다운로드 큐에 추가되었습니다.")

    def start_selected(self):
        """선택된 항목 다운로드 시작"""
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()))

        if not selected_rows:
            QMessageBox.warning(self, "선택 없음", "다운로드할 항목을 선택해주세요.")
            return

        started_count = 0
        for row in selected_rows:
            # 이미 실행 중인지 확인
            if row in self.workers:
                continue

            # 다운로드 시작
            url = self.table.item(row, 0).text()
            save_dir = self.table.item(row, 1).text()
            filename = self.table.item(row, 2).text()
            format_text = self.table.item(row, 3).text()

            # 형식 텍스트에서 다운로드 타입 추출
            if "오디오" in format_text:
                download_type = 'audio'
            elif "최고 화질" in format_text:
                download_type = 'video_best'
            elif "720p" in format_text:
                download_type = 'video_720p'
            elif "480p" in format_text:
                download_type = 'video_480p'
            else:
                download_type = 'audio'

            # 출력 경로
            output_path = os.path.join(save_dir, filename)

            # 워커 생성 및 시작
            worker = YoutubeDownloadWorker(url, output_path, download_type)
            worker.progress.connect(lambda msg, r=row: self._update_progress(r, msg))
            worker.title_resolved.connect(lambda title, r=row: self._update_title(r, title))
            worker.file_path_resolved.connect(lambda path, r=row: self._update_file_path(r, path))
            worker.finished.connect(lambda success, msg, r=row: self._on_finished(r, success, msg))

            self.workers[row] = worker
            worker.start()

            self.table.item(row, 5).setText("시작 중...")
            started_count += 1

        if started_count > 0:
            QMessageBox.information(self, "다운로드 시작", f"{started_count}개 항목의 다운로드를 시작했습니다.")
        else:
            QMessageBox.warning(self, "이미 실행 중", "선택한 항목이 이미 다운로드 중입니다.")

    def _update_progress(self, row: int, message: str):
        """진행 상태 업데이트"""
        if row < self.table.rowCount():
            self.table.item(row, 5).setText(message)

    def _update_title(self, row: int, title: str):
        """영상 제목으로 파일명 업데이트"""
        if row < self.table.rowCount():
            # 현재 파일명이 기본값인 경우에만 업데이트
            current_filename = self.table.item(row, 2).text()
            if current_filename.startswith("download"):
                # 제목을 안전한 파일명으로 변환
                safe_title = self._sanitize_filename(title)[:60]

                # 현재 확장자 유지
                _, ext = os.path.splitext(current_filename)
                new_filename = safe_title + ext

                self.table.item(row, 2).setText(new_filename)

                # 파일 경로도 업데이트 (임시, 실제 경로는 file_path_resolved에서 업데이트)
                save_dir = self.table.item(row, 1).text()
                self.file_paths[row] = os.path.join(save_dir, new_filename)

    def _update_file_path(self, row: int, file_path: str):
        """실제 다운로드된 파일 경로 업데이트"""
        if row < self.table.rowCount():
            # 실제 파일 경로 저장
            self.file_paths[row] = file_path

            # 파일명도 업데이트 (실제 다운로드된 파일명으로)
            filename = os.path.basename(file_path)
            self.table.item(row, 2).setText(filename)

    def _on_finished(self, row: int, success: bool, message: str):
        """다운로드 완료 처리"""
        if row < self.table.rowCount():
            if success:
                self.table.item(row, 5).setText("✓ 완료")
            else:
                self.table.item(row, 5).setText(f"✗ 실패: {message}")

        # 워커 정리
        if row in self.workers:
            self.workers[row].wait()
            self.workers[row].deleteLater()
            del self.workers[row]

    def stop_selected(self):
        """선택된 항목 다운로드 중지"""
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()))

        if not selected_rows:
            QMessageBox.warning(self, "선택 없음", "중지할 항목을 선택해주세요.")
            return

        stopped_count = 0
        for row in selected_rows:
            if row in self.workers:
                worker = self.workers[row]
                worker.cancel()

                # 타임아웃 설정하여 데드락 방지 (최대 2초 대기)
                if not worker.wait(2000):
                    # 2초 후에도 종료되지 않으면 강제 종료
                    worker.terminate()
                    worker.wait(1000)  # 종료 확인 (1초)

                worker.deleteLater()
                del self.workers[row]
                self.table.item(row, 5).setText("중지됨")
                stopped_count += 1

        if stopped_count > 0:
            QMessageBox.information(self, "다운로드 중지", f"{stopped_count}개 항목을 중지했습니다.")
        else:
            QMessageBox.warning(self, "실행 중 아님", "선택한 항목 중 다운로드 중인 항목이 없습니다.")

    def remove_selected(self):
        """선택된 항목 제거"""
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()), reverse=True)

        if not selected_rows:
            QMessageBox.warning(self, "선택 없음", "제거할 항목을 선택해주세요.")
            return

        for row in selected_rows:
            # 실행 중인 워커가 있으면 중지
            if row in self.workers:
                worker = self.workers[row]
                worker.cancel()

                # 타임아웃 설정하여 데드락 방지 (최대 2초 대기)
                if not worker.wait(2000):
                    # 2초 후에도 종료되지 않으면 강제 종료
                    worker.terminate()
                    worker.wait(1000)  # 종료 확인 (1초)

                worker.deleteLater()
                del self.workers[row]

            # 파일 경로 정보 삭제
            if row in self.file_paths:
                del self.file_paths[row]

            # 행 제거
            self.table.removeRow(row)

        QMessageBox.information(self, "제거 완료", f"{len(selected_rows)}개 항목을 제거했습니다.")

    def clear_completed(self):
        """완료된 항목 정리"""
        rows_to_remove = []
        for row in range(self.table.rowCount()):
            status = self.table.item(row, 5).text()
            if "완료" in status or "실패" in status:
                rows_to_remove.append(row)

        # 뒤에서부터 제거
        for row in reversed(rows_to_remove):
            # 파일 경로 정보 삭제
            if row in self.file_paths:
                del self.file_paths[row]
            self.table.removeRow(row)

        if rows_to_remove:
            QMessageBox.information(self, "정리 완료", f"{len(rows_to_remove)}개 항목을 정리했습니다.")
        else:
            QMessageBox.information(self, "정리 완료", "정리할 항목이 없습니다.")

    def _on_double_click(self, row: int, column: int):
        """더블클릭 시 파일 재생"""
        # 완료된 파일만 재생
        status = self.table.item(row, 5).text()
        if "완료" not in status:
            QMessageBox.information(self, "재생 불가", "다운로드가 완료된 파일만 재생할 수 있습니다.")
            return

        # 파일 재생
        self._play_file(row)

    def closeEvent(self, event):
        """앱 종료 시 모든 워커 중지"""
        for worker in self.workers.values():
            worker.cancel()

            # 타임아웃 설정하여 데드락 방지 (최대 2초 대기)
            if not worker.wait(2000):
                # 2초 후에도 종료되지 않으면 강제 종료
                worker.terminate()
                worker.wait(1000)  # 종료 확인 (1초)

        event.accept()


def main():
    # 의존성 확인 및 자동 설치
    print("=" * 60)
    print("Youtube Downloader 시작 중...")
    print("=" * 60)

    checker = DependencyChecker()
    if not checker.check_and_install():
        print("\n경고: 일부 의존성 설치에 실패했습니다.")
        print("앨범 아트 기능이 제대로 작동하지 않을 수 있습니다.")
        print("수동으로 FFmpeg와 AtomicParsley를 설치해주세요.\n")

    app = QApplication(sys.argv)
    window = YoutubeDownloaderApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
