"""
면학 불참 계획 관리자 자동 설치 및 빌드 스크립트 (v5 Final)
이 스크립트는 다음 작업을 자동으로 수행합니다:
1. 필요한 Python 패키지 설치 (holidays, pyinstaller)
2. 메인 프로그램 파일 생성 (myeonhak_final.py)
3. PyInstaller 를 통해 Windows 실행 파일 (.exe) 생성
4. 결과 확인

사용법:
  python setup_final.py

주의: 이 스크립트는 Windows 환경에서 실행해야 합니다.
"""

import subprocess
import sys
import os
import shutil

def run_command(command, description):
    """명령어를 실행하고 결과를 출력"""
    print(f"\n[+] {description}...")
    print(f"    명령어: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        print(f"    ✅ 성공!")
        if result.stdout:
            # 로그가 너무 길지 않도록 일부만 출력
            lines = result.stdout.strip().split('\n')
            for line in lines[-5:]:  # 마지막 5 줄만 출력
                if line.strip():
                    print(f"       {line}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"    ❌ 실패: {e}")
        if e.stderr:
            print(f"    오류 메시지: {e.stderr[:200]}...")
        return False
    except Exception as e:
        print(f"    ❌ 예상치 못한 오류: {e}")
        return False

def main():
    print("=" * 60)
    print("   면학 불참 계획 관리자 - 자동 설치 및 빌드 스크립트")
    print("=" * 60)
    
    # 1. Python 버전 확인
    print(f"\n[1] Python 버전 확인 중...")
    print(f"    현재 Python: {sys.version}")
    
    # 2. 필요 패키지 설치
    packages = ["holidays", "pyinstaller"]
    for pkg in packages:
        cmd = [sys.executable, "-m", "pip", "install", pkg, "--upgrade", "--quiet"]
        if not run_command(cmd, f"{pkg} 설치/업데이트"):
            print(f"\n⚠️  {pkg} 설치에 실패했지만 계속 진행합니다.")
    
    # 3. 메인 스크립트 확인
    script_name = "myeonhak_final.py"
    if not os.path.exists(script_name):
        print(f"\n[!] {script_name} 파일을 찾을 수 없습니다.")
        print("    같은 폴더에 myeonhak_final.py 가 있는지 확인해주세요.")
        input("\n계속하려면 엔터를 누르세요...")
        return
    
    print(f"\n[2] {script_name} 파일 확인됨 ✅")
    
    # 4. PyInstaller 로 EXE 생성
    print("\n[3] Windows 실행 파일 (.exe) 생성 중...")
    print("    이 작업은 몇 분 정도 소요될 수 있습니다.")
    
    build_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "MyeonhakCalendar",
        "--add-data", "myeonhak_data.json;." if os.path.exists("myeonhak_data.json") else "",
        "--encoding", "utf-8",
        script_name
    ]
    
    # 빈 인수는 제거
    build_cmd = [arg for arg in build_cmd if arg != ""]
    
    if run_command(build_cmd, "EXE 파일 빌드"):
        print("\n" + "=" * 60)
        print("   🎉 빌드가 성공적으로 완료되었습니다!")
        print("=" * 60)
        
        # 결과 확인
        dist_folder = "dist"
        exe_path = os.path.join(dist_folder, "MyeonhakCalendar.exe")
        
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"\n📦 생성된 파일: {exe_path}")
            print(f"   크기: {file_size:.2f} MB")
            print(f"\n💡 사용 방법:")
            print(f"   - 'dist' 폴더의 'MyeonhakCalendar.exe' 를 실행하세요.")
            print(f"   - 첫 실행 시 방화벽 경고가 나올 수 있으니 '허용'을 눌러주세요.")
        else:
            print("\n⚠️  EXE 파일이 생성되지 않았습니다. 로그를 확인해주세요.")
    else:
        print("\n❌ 빌드에 실패했습니다. 아래 사항을 확인해주세요:")
        print("   1. Python 이 정상 설치되었는지 확인 (3.6 이상 권장)")
        print("   2. 인터넷 연결 상태 확인 (패키지 다운로드 필요)")
        print("   3. 백신 프로그램이 PyInstaller 를 차단하지 않는지 확인")
    
    print("\n" + "=" * 60)
    input("작업을 완료했습니다. 엔터를 누르면 창이 닫힙니다...")

if __name__ == "__main__":
    # 인코딩 설정 (Windows 에서 UTF-8 보장)
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    main()
