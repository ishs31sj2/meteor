# 면학 불참 계획 관리자 Ultimate - Windows 설치 가이드

## 🎉 새로운 기능 (v4)

### 1. 실시간 시계 동기화
- 상단에 현재 시간을 초단위로 표시
- 프로그램 실행 중 자동 갱신

### 2. 한국 공휴일 자동 연동
- `holidays` 라이브러리를 사용하여 매년 자동 업데이트
- 달력에 공휴일은 빨간색 + 이름으로 표시
- 예: 설날, 추석, 삼일절, 광복절 등

### 3. 알람 기능
- ⏰ 버튼으로 알람 설정 가능
- 지정된 시간에 팝업 메시지 + 사운드 경고
- 복수 알람 등록 가능

### 4. 바탕화면 메모 동기화
- 📝 버튼 클릭 시 현재 선택 날짜의 계획이 바탕화면의 `면학_메모.txt` 로 저장됨
- Windows 바탕화면에서 바로 확인 가능

---

## 🔧 오류 해결: "pyinstaller 용어가 인식되지 않습니다"

이전 버전에서 발생했던 오류는 **인코딩 문제**였습니다.  
새로운 `build_windows_v4.bat` 파일은 UTF-8 인코딩을 올바르게 처리합니다.

### 올바른 실행 방법:

1. **파일 다운로드**: `myeonhak_calendar_v4.py` 와 `build_windows_v4.bat` 을 Windows 로 전송
   
2. **배치 파일 실행**: 
   - `build_windows_v4.bat` 을 **더블클릭**
   - 자동으로 다음 작업 수행:
     - Python 설치 확인
     - `holidays`, `pyinstaller` 패키지 자동 설치
     - `MyeonhakCalendar.exe` 생성

3. **프로그램 사용**:
   - 생성된 `dist\MyeonhakCalendar.exe` 실행

---

## 📦 ZIP 파일 구성

```
MyeonhakCalendar_Ultimate.zip
├── myeonhak_calendar_v4.py      # 메인 프로그램 (최신 버전)
├── build_windows_v4.bat         # 자동 빌드 스크립트 (인코딩 수정됨)
├── requirements.txt             # 필요 패키지 목록
└── README.md                    # 이 파일
```

---

## 🚀 빠른 시작 (Windows)

### 단계 1: Python 설치 (미설치 시)
1. https://www.python.org/downloads/ 접속
2. Python 3.x 다운로드 (권장: 최신 안정 버전)
3. 설치 시 **"Add Python to PATH" 체크 필수!**

### 단계 2: 자동 빌드 실행
```
build_windows_v4.bat 더블클릭
```

### 단계 3: 프로그램 실행
```
dist\MyeonhakCalendar.exe 실행
```

---

## 💡 사용법

### 달력 조작
- `<`, `>` 버튼: 이전/다음 월 이동
- `오늘` 버튼: 현재 날짜로 이동
- 날짜 클릭: 해당 날짜의 상세 정보 보기/편집

### 면학 설정 (평일만 가능)
1. 평일 날짜 선택
2. "8 면", "1 면", "2 면" 체크박스 선택
3. `저장` 버튼 클릭

### 할 일 관리
- 입력창에 작성 후 엔터 또는 `추가` 버튼
- 더블클릭: 완료/미완료 토글
- `삭제` 버튼: 선택 항목 삭제

### 알람 설정
1. `⏰ 알람 설정` 버튼 클릭
2. 시간 (HH:MM 형식) 과 메시지 입력
3. `설정` 버튼 클릭
4. 활성 알람 수가 하단에 표시됨

### 바탕화면 메모 동기화
1. 원하는 날짜 선택
2. `📝 바탕화면 메모 동기화` 버튼 클릭
3. 바탕화면에 `면학_메모.txt` 생성/업데이트

---

## 🐛 문제 해결

### Q: "Python 이 설치되어 있지 않습니다" 오류
A: Python 을 설치하고, 설치 시 "Add Python to PATH"를 체크하세요. 재설치가 필요할 수 있습니다.

### Q: "pip install 오류" 발생
A: 관리자 권한으로 CMD 를 실행한 후 다음 명령어 수동 실행:
```cmd
python -m pip install --upgrade pip
pip install holidays pyinstaller
```

### Q: EXE 가 생성되지 않음
A: `build_windows_v4.bat` 을 우클릭 → `다른 이름으로 실행` → `관리자 권한`으로 실행해보세요.

### Q: 공휴일이 표시되지 않음
A: 인터넷 연결 후 프로그램을 재실행하면 `holidays` 라이브러리가 최신 공휴일 정보를 다운로드합니다.

---

## 📝 기술 정보

- **언어**: Python 3.x
- **GUI**: Tkinter (표준 라이브러리)
- **데이터 저장**: JSON (`myeonhak_data.json`)
- **외부 라이브러리**: 
  - `holidays`: 한국 공휴일 정보
  - `pyinstaller`: EXE 패키징
- **플랫폼**: Windows 10/11 권장 (Windows 7 도 가능)

---

## 📞 지원

문제가 지속되면:
1. 배치 파일 실행 시 콘솔 전체 메시지 캡처
2. Python 버전 확인 (`python --version`)
3. 위 정보를 포함하여 문의
