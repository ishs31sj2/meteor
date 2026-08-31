# 면학 불참 계획 관리자 (Myeonhak Calendar)

## 📋 프로그램 소개
면학 시간 (8 면, 1 면, 2 면) 불참 계획을 관리하는 달력 기반 프로그램입니다.

### ✨ 주요 기능
- **실시간 시계**: 현재 시간을 초단위로 표시
- **한국 공휴일 자동 연동**: `holidays` 라이브러리를 통해 매년 자동 업데이트되는 공휴일 정보 제공
- **월간 달력 뷰**: 직관적인 달력 인터페이스
- **면학 계획 관리**: 8 면/1 면/2 면 불참·참가 상태 및 메모 등록
- **할 일 관리**: 날짜별 할 일 추가, 완료 처리, 삭제
- **시각적 인디케이터**: 면학 종류별 색상 코드 (🔴 8 면, 🔵 1 면, 🟡 2 면)
- **자동 저장**: 모든 데이터는 JSON 파일에 실시간 저장

---

## 🚀 Windows 에서 실행 파일 (.exe) 만들기

### 방법 1: 자동 빌드 스크립트 사용 (권장)

1. **Python 설치 확인**
   - Python 3.8 이상이 설치되어 있어야 합니다.
   - https://www.python.org/downloads/ 에서 다운로드 가능

2. **빌드 스크립트 실행**
   - `build_windows.bat` 파일을 더블클릭합니다.
   - 자동으로 필요한 패키지가 설치되고 EXE 파일이 생성됩니다.

3. **생성된 EXE 실행**
   - `dist` 폴더의 `MyeonhakCalendar.exe` 를 실행합니다.

### 방법 2: 수동으로 실행

Windows PowerShell 또는 CMD 에서 다음 명령어를 순서대로 실행하세요:

```powershell
# 1. 필요한 패키지 설치
pip install holidays pyinstaller

# 2. EXE 파일 생성
pyinstaller --onefile --windowed --name "MyeonhakCalendar" myeonhak_calendar_v3.py

# 3. 생성된 파일 실행
# dist\MyeonhakCalendar.exe 를 더블클릭하거나 명령어로 실행
```

---

## 📁 파일 구성

```
MyeonhakCalendar_Dist/
├── myeonhak_calendar_v3.py    # 메인 프로그램 소스
├── build_windows.bat          # Windows 자동 빌드 스크립트
├── README_WINDOWS.md          # 이 파일 (사용 가이드)
└── requirements.txt           # 필요 패키지 목록
```

### 필요 패키지 (requirements.txt)
```
holidays>=0.40
pyinstaller>=6.0
```

---

## 💡 사용 방법

1. **프로그램 실행**
   - `MyeonhakCalendar.exe` 를 더블클릭

2. **달력 탐색**
   - `<`, `>` 버튼으로 월 이동
   - "오늘" 버튼으로 현재 날짜로 이동

3. **날짜 선택**
   - 달력의 원하는 날짜 클릭

4. **면학 계획 설정**
   - 오른쪽 패널에서 8 면/1 면/2 면 체크박스 선택
   - 메모 입력 (자동 저장)

5. **할 일 관리**
   - 할 일 입력 후 "+" 버튼 또는 Enter 키로 추가
   - 더블클릭으로 완료/미완료 토글
   - "선택 항목 삭제" 버튼으로 삭제

6. **공휴일 확인**
   - 공휴일은 빨간색으로 표시되며 이름이 함께 표시됩니다.

---

## 🔧 문제 해결

### Q: "pyinstaller 용어가 인식되지 않습니다" 오류
**해결방법:**
```powershell
pip install pyinstaller
```
위 명령어를 실행한 후 다시 시도하세요.

### Q: "holidays 모듈을 찾을 수 없습니다" 오류
**해결방법:**
```powershell
pip install holidays
```

### Q: EXE 가 실행되지 않습니다
**해결방법:**
- Windows Defender 또는 백신 프로그램이 차단했을 수 있습니다.
- `dist\MyeonhakCalendar.exe` 를 예외 처리해주세요.

### Q: 공휴일이 업데이트되지 않습니다
**해결방법:**
- `holidays` 라이브러리가 최신 버전인지 확인:
```powershell
pip install --upgrade holidays
```

---

## 📝 데이터 저장 위치

모든 데이터는 프로그램 실행 폴더의 `myeonhak_data.json` 파일에 저장됩니다.
백업하려면 이 파일을 복사해두세요.

---

## 📄 라이선스

이 프로그램은 교육 목적으로 제작되었습니다.
