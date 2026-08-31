@echo off
chcp 65001 >nul
echo ========================================
echo 면학 불참 계획 관리자 - Windows 빌드 도구
echo ========================================
echo.

:: Python 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python 이 설치되어 있지 않습니다.
    echo https://www.python.org/downloads/ 에서 Python 3.8 이상을 설치해주세요.
    pause
    exit /b 1
)

echo [1/3] Python 버전 확인 완료
python --version

:: 필요한 패키지 설치
echo.
echo [2/3] 필요한 패키지 설치 중...
pip install holidays pyinstaller --quiet

:: PyInstaller 로 EXE 생성
echo.
echo [3/3] 실행 파일 (.exe) 생성 중...
pyinstaller --onefile --windowed --name "MyeonhakCalendar" --icon=NONE myeonhak_calendar_v3.py

if exist "dist\MyeonhakCalendar.exe" (
    echo.
    echo ========================================
    echo ✅ 성공적으로 EXE 파일이 생성되었습니다!
    echo ========================================
    echo.
    echo 위치: %CD%\dist\MyeonhakCalendar.exe
    echo.
    echo 이제 dist 폴더의 MyeonhakCalendar.exe 를 실행하시면 됩니다.
    echo.
) else (
    echo.
    echo [오류] EXE 파일 생성에 실패했습니다.
    echo 로그를 확인해주세요.
)

pause
