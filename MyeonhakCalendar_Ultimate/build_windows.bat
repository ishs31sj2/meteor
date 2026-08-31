@echo off
chcp 65001 >nul
echo ========================================
echo   면학 불참 계획 관리자 - Ultimate
echo   Windows 자동 빌드 스크립트
echo ========================================
echo.

REM Python 설치 확인
echo [1/4] Python 설치 확인 중...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 오류: Python 이 설치되어 있지 않습니다!
    echo Python 3.8 이상을 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✓ Python 설치됨
python --version
echo.

REM 필요 패키지 설치
echo [2/4] 필요 패키지 설치 중...
echo.
pip install --upgrade pip
pip install holidays pyinstaller
if %errorlevel% neq 0 (
    echo 오류: 패키지 설치 실패
    pause
    exit /b 1
)
echo ✓ 패키지 설치 완료
echo.

REM PyInstaller 로 EXE 생성
echo [3/4] EXE 파일 생성 중...
echo.
pyinstaller --onefile --windowed --name "MyeonhakCalendar_Ultimate" --icon=NONE myeonhak_calendar_ultimate.py
if %errorlevel% neq 0 (
    echo 오류: EXE 생성 실패
    pause
    exit /b 1
)
echo.

REM 결과 확인
echo [4/4] 생성 완료!
echo.
if exist "dist\MyeonhakCalendar_Ultimate.exe" (
    echo ✓ EXE 파일이 성공적으로 생성되었습니다!
    echo 위치: %cd%\dist\MyeonhakCalendar_Ultimate.exe
    echo.
    echo 파일을 복사하여 원하는 곳에 사용하세요.
    echo.
    dir dist\MyeonhakCalendar_Ultimate.exe
) else (
    echo 오류: EXE 파일을 찾을 수 없습니다.
    echo dist 폴더를 확인해주세요.
)

echo.
echo ========================================
echo 빌드가 완료되었습니다!
echo ========================================
pause
