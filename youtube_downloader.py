#!/usr/bin/env python3
"""
유튜브 영상을 고음질 M4A 오디오로 다운로드하는 프로그램
"""

import os
import sys
from pathlib import Path
import yt_dlp


def download_youtube_audio(url, output_path='downloads'):
    """
    유튜브 영상에서 고음질 오디오를 M4A 형식으로 다운로드

    Args:
        url: 유튜브 영상 URL
        output_path: 다운로드 폴더 경로 (기본값: 'downloads')
    """
    # 다운로드 폴더 생성
    Path(output_path).mkdir(parents=True, exist_ok=True)

    # yt-dlp 옵션 설정
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',  # 최고 음질의 m4a 또는 최고 오디오
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),  # 출력 파일명 형식
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # 오디오 추출
            'preferredcodec': 'm4a',  # M4A 형식으로 변환
            'preferredquality': '0',  # 최고 품질 (0 = 원본 품질)
        }],
        'quiet': False,  # 진행 상황 표시
        'no_warnings': False,
        'ignoreerrors': False,
    }

    try:
        print(f"\n유튜브 영상 다운로드 시작: {url}\n")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 영상 정보 가져오기
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)

            print(f"제목: {video_title}")
            print(f"길이: {duration // 60}분 {duration % 60}초")
            print(f"다운로드 폴더: {output_path}\n")

            # 다운로드 실행
            ydl.download([url])

        print(f"\n✓ 다운로드 완료!")
        print(f"파일 위치: {output_path}/{video_title}.m4a")

    except Exception as e:
        print(f"\n✗ 오류 발생: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main():
    """메인 함수"""
    print("=" * 60)
    print("유튜브 고음질 오디오 다운로더 (M4A)")
    print("=" * 60)

    # 명령줄 인자로 URL 받기
    if len(sys.argv) > 1:
        url = sys.argv[1]
        # 두 번째 인자로 출력 폴더를 받을 수 있음
        output_path = sys.argv[2] if len(sys.argv) > 2 else 'downloads'
    else:
        # 사용자 입력 받기
        url = input("\n유튜브 URL을 입력하세요: ").strip()
        if not url:
            print("URL이 입력되지 않았습니다.", file=sys.stderr)
            sys.exit(1)
        # 출력 폴더 설정
        output_path = input("다운로드 폴더 (기본값: downloads): ").strip() or 'downloads'

    # 다운로드 실행
    download_youtube_audio(url, output_path)


if __name__ == "__main__":
    main()
