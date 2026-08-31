"""
면학 불참 계획 관리자 v5 - 자동 설치 및 빌드 스크립트
이 스크립트는 필요한 패키지를 설치하고, 실행 파일 (.exe) 을 생성합니다.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def run_command(command, description):
    """명령어를 실행하고 결과를 출력"""
    print(f"\n[INFO] {description}...")
    print(f"Command: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 실패: {e}")
        if e.stderr:
            print(e.stderr)
        return False
    except Exception as e:
        print(f"[ERROR] 예외 발생: {e}")
        return False

def main():
    print("="*60)
    print("면학 불참 계획 관리자 v5 - 자동 설치 및 빌드")
    print("="*60)

    # 1. Python 버전 확인
    print("\n[STEP 1] Python 버전 확인")
    print(f"Python Version: {sys.version}")

    # 2. 필요 패키지 설치
    print("\n[STEP 2] 필요 패키지 설치 (tkinter, holidays, pyinstaller)")
    # tkinter 는 기본 포함됨 (Windows 기준)
    packages = ['holidays', 'pyinstaller']
    
    for pkg in packages:
        cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', pkg]
        if not run_command(cmd, f"{pkg} 설치 중"):
            print(f"[WARNING] {pkg} 설치에 실패했지만 계속 진행합니다.")

    # 3. 메인 스크립트 확인
    script_path = Path(__file__).parent / "main.py"
    if not script_path.exists():
        print(f"[ERROR] main.py 파일을 찾을 수 없습니다: {script_path}")
        print("main.py 가 현재 디렉토리에 있는지 확인해주세요.")
        input("계속하려면 Enter 를 누르세요...")
        return

    print(f"\n[STEP 3] 메인 스크립트 확인 완료: {script_path}")

    # 4. PyInstaller 로 EXE 생성
    print("\n[STEP 4] PyInstaller 로 EXE 파일 생성 중...")
    dist_dir = Path(__file__).parent / "dist"
    build_dir = Path(__file__).parent / "build"
    
    # 이전 빌드 정리 (선택사항)
    if dist_dir.exists():
        print("기존 dist 폴더 정리 중...")
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        print("기존 build 폴더 정리 중...")
        shutil.rmtree(build_dir)

    # PyInstaller 명령어 구성
    # --onefile: 단일 파일로 생성
    # --windowed: 콘솔 창 숨김 (GUI 전용)
    # --name: 출력 파일 이름
    # --add-data: 데이터 파일 포함 (필요시)
    # --hidden-import: 숨겨진 임포트 명시 (holidays 등)
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name', 'MyeonhakCalendar_v5',
        '--hidden-import', 'holidays',
        '--hidden-import', 'tkinter',
        '--encoding', 'utf-8',
        str(script_path)
    ]

    if run_command(cmd, "EXE 파일 생성 중"):
        print("\n" + "="*60)
        print("✅ 성공적으로 EXE 파일이 생성되었습니다!")
        print("="*60)
        exe_path = dist_dir / "MyeonhakCalendar_v5.exe"
        if exe_path.exists():
            print(f"\n📍 위치: {exe_path}")
            print(f"📊 크기: {exe_path.stat().st_size / (1024*1024):.2f} MB")
            print("\n💡 사용 방법:")
            print(f"   '{exe_path}' 파일을 더블클릭하여 프로그램을 실행하세요.")
            print("   첫 실행 시 방화벽 경고가 뜰 수 있으니 '허용'을 눌러주세요.")
        else:
            print("\n[WARNING] EXE 파일이 생성되지 않았습니다. 로그를 확인하세요.")
    else:
        print("\n[ERROR] EXE 파일 생성에 실패했습니다.")
        print("다음 사항을 확인하세요:")
        print("  1. Python 이 정상 설치되었는지 확인 (python --version)")
        print("  2. 인터넷 연결 상태 확인 (패키지 다운로드 필요)")
        print("  3. 백신 프로그램이 PyInstaller 를 차단하지 않는지 확인")
    
    print("\n" + "="*60)
    input("완료! Enter 키를 누르면 창이 닫힙니다...")

if __name__ == "__main__":
    # 인코딩 문제 방지를 위해 UTF-8 명시 (Windows 환경)
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    main()
