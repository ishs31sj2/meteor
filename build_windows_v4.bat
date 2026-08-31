@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ========================================
echo   면학 불참 계획 관리자 - Windows 빌더
echo ========================================
echo.

REM Python 설치 확인
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python 이 설치되어 있지 않습니다.
    echo https://www.python.org/downloads/ 에서 Python 3.x 를 설치해주세요.
    echo 설치 시 "Add Python to PATH"를 체크해주세요.
    pause
    exit /b 1
)

echo [확인] Python 이 설치되어 있습니다.
python --version
echo.

REM 필요한 패키지 설치
echo [진행] 필요한 패키지를 설치합니다...
pip install holidays pyinstaller --quiet
if %errorlevel% neq 0 (
    echo [경고] 패키지 설치 중 일부 오류가 발생했지만 계속 진행합니다.
)
echo [완료] 패키지 설치 완료
echo.

REM PyInstaller 로 EXE 생성
echo [진행] EXE 파일을 생성합니다 (약 1-2 분 소요)...
pyinstaller --onefile --windowed --name "MyeonhakCalendar" --icon=NONE myeonhak_calendar_v4.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   [성공] EXE 파일이 생성되었습니다!
    echo   위치: dist\MyeonhakCalendar.exe
    echo ========================================
    echo.
    echo 이제 dist 폴더의 MyeonhakCalendar.exe 를 실행하시면 됩니다.
) else (
    echo.
    echo ========================================
    echo   [오류] EXE 생성 중 문제가 발생했습니다.
    echo   아래 메시지를 확인해주세요.
    echo ========================================
)

echo.
pause
