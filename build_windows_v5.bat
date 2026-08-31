@echo off
chcp 65001 > nul
echo ========================================
echo   MyeonhakCalendar Build Script v5
echo ========================================
echo.

REM Python 확인
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 이 설치되어 있지 않습니다.
    echo https://www.python.org/downloads/ 에서 설치해주세요.
    pause
    exit /b 1
)

echo [OK] Python 이 감지되었습니다.
echo.

REM 필요한 패키지 설치
echo [STEP 1] 필요한 패키지를 설치합니다...
pip install holidays pyinstaller --quiet
if %errorlevel% neq 0 (
    echo [ERROR] 패키지 설치에 실패했습니다.
    pause
    exit /b 1
)
echo [OK] 패키지 설치가 완료되었습니다.
echo.

REM PyInstaller 로 EXE 생성
echo [STEP 2] EXE 파일을 생성합니다...
pyinstaller --onefile --windowed --name "MyeonhakCalendar" myeonhak_calendar_v5.py
if %errorlevel% neq 0 (
    echo [ERROR] EXE 생성에 실패했습니다.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] MyeonhakCalendar.exe 생성 완료!
echo ========================================
echo.
echo 생성된 파일 위치: dist\MyeonhakCalendar.exe
echo.
echo 프로그램을 실행하시려면 dist 폴더의
echo MyeonhakCalendar.exe 를 실행해주세요.
echo ========================================
pause
