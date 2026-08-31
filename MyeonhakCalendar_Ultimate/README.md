# 📅 면학 불참 계획 관리자 - Ultimate Edition

## 🎉 새로운 기능 (v3.0 Ultimate)

### ✨ 주요 개선사항
1. **실시간 시계 동기화** - 상단에 현재 시간을 초단위로 표시
2. **한국 공휴일 자동 연동** - `holidays` 라이브러리로 매년 자동 업데이트
3. **알람 기능** - 원하는 시간에 알림 설정 가능
4. **바탕화면 메모 동기화** - 오늘 일정을 바탕화면 텍스트 파일로 자동 생성
5. **모던 다크 테마 UI** - 세련로운 디자인과 색상 코드
6. **시험 일정 관리** - 날짜별 시험 과목 등록

### 📋 기본 기능
- 월간 달력 뷰에서 직관적인 일정 관리
- 8 면/1 면/2 면 불참·참가 설정
- 날짜별 할 일 목록 (추가, 완료 처리, 삭제)
- 메모 작성 및 저장
- 자동 데이터 저장 (JSON 형식)
- 데이터 백업 기능

---

## 🚀 Windows 에서 EXE 생성하기

### 방법 1: 자동 빌드 스크립트 사용 (권장)

1. **파일 준비**
   - `MyeonhakCalendar_Ultimate` 폴더 전체를 Windows PC 로 복사

2. **자동 빌드 실행**
   - `build_windows.bat` 파일을 **더블클릭**
   - 자동으로 다음 작업이 수행됩니다:
     - Python 설치 확인
     - 필요 패키지 자동 설치 (`holidays`, `pyinstaller`)
     - EXE 파일 생성

3. **완료!**
   - `dist` 폴더에 `MyeonhakCalendar_Ultimate.exe` 가 생성됩니다
   - 이 파일을 원하는 곳으로 복사하여 사용

### 방법 2: 수동 빌드

```cmd
# 1. 명령 프롬프트 (CMD) 를 관리자 권한으로 실행

# 2. 패키지 설치
pip install holidays pyinstaller

# 3. EXE 생성
pyinstaller --onefile --windowed --name "MyeonhakCalendar_Ultimate" myeonhak_calendar_ultimate.py

# 4. dist 폴더에서 exe 파일 확인
```

---

## ⚠️ 자주 발생하는 오류 해결

### 오류 1: "pyinstaller 용어가 인식되지 않습니다"
**원인**: PyInstaller 가 설치되지 않음  
**해결**: 
```cmd
pip install pyinstaller
```
또는 `build_windows.bat` 을 실행하면 자동 설치됩니다!

### 오류 2: "Python 이 설치되어 있지 않습니다"
**해결**: 
1. https://www.python.org/downloads/ 에서 Python 3.8 이상 다운로드
2. 설치 시 **"Add Python to PATH"** 체크박스 반드시 선택!
3. 재시작 후 다시 시도

### 오류 3: "holidays 모듈을 찾을 수 없습니다"
**해결**:
```cmd
pip install holidays
```

### 오류 4: EXE 가 생성되지 않음
**확인할 사항**:
- `build_windows.bat` 실행 중 오류 메시지 확인
- `build` 폴더와 `dist` 폴더 확인
- antivirus 프로그램이 차단하지 않는지 확인
- 관리자 권한으로 실행해보기

---

## 💡 사용 가이드

### 1. 달력에서 날짜 선택
- 월간 달력에서 원하는 날짜 클릭
- 주말은 주황색/빨간색, 공휴일은 빨간색으로 표시

### 2. 면학 계획 설정
- 오른쪽 패널에서 8 면/1 면/2 면 체크박스 선택
- 자동으로 저장되며 달력에 표시됩니다

### 3. 할 일 관리
- 할 일 입력창에 작성 후 Enter 또는 "추가" 버튼
- 더블클릭으로 완료/미완료 토글
- "삭제" 버튼으로 제거

### 4. 알람 설정
- 하단 "⏰ 알람 설정" 버튼 클릭
- 시간 (HH:MM 형식) 과 메시지 입력
- 해당 시간에 알림 팝업 및 사운드 발생

### 5. 바탕화면 메모 동기화
- 하단 "📝 바탕화면 메모 동기화" 버튼 클릭
- 바탕화면에 `면학_메모.txt` 파일 생성/업데이트
- 오늘 일정이 텍스트로 정리됨

### 6. 데이터 백업
- 하단 "💾 데이터 백업" 버튼 클릭
- 현재 날짜/시간이 포함된 JSON 파일로 저장

---

## 📁 파일 구조

```
MyeonhakCalendar_Ultimate/
├── myeonhak_calendar_ultimate.py   # 메인 프로그램 소스
├── build_windows.bat                # Windows 자동 빌드 스크립트
├── requirements.txt                 # 필요 패키지 목록
├── README.md                        # 이 파일
├── dist/                            # 빌드 후 생성되는 폴더
│   └── MyeonhakCalendar_Ultimate.exe
└── build/                           # 빌드 중간 파일 (삭제 가능)
```

생성되는 데이터 파일:
- `myeonhak_data.json` - 일정 데이터
- `myeonhak_config.json` - 설정 (알람 등)

---

## 🎨 UI 특징

- **다크 테마**: 눈이 편안한 어두운 배경
- **색상 코드**:
  - 8 면: 빨강 (#e74c3c)
  - 1 면: 민트 (#4ecca3)
  - 2 면: 노랑 (#f1c40f)
  - 공휴일/주말: 빨강
  - 토요일: 주황
- **실시간 시계**: 우측 상단에 현재 시간 표시
- **반응형 디자인**: 창 크기 조절 가능

---

## 🔧 기술 정보

- **언어**: Python 3.8+
- **GUI 프레임워크**: Tkinter
- **필수 패키지**: 
  - `holidays` (한국 공휴일)
  - `pyinstaller` (EXE 패키징)
- **플랫폼**: Windows 10/11 (권장), Linux, macOS

---

## 📞 문제 해결

빌드나 실행 중 문제가 발생하면:

1. **오류 메시지 캡처**: 전체 오류 메시지를 확인
2. **Python 버전 확인**: `python --version` 실행
3. **패키지 재설치**: 
   ```cmd
   pip uninstall holidays pyinstaller
   pip install holidays pyinstaller
   ```
4. **관리자 권한 실행**: CMD 를 관리자 권한으로 실행

---

## 📜 라이선스

본 프로그램은 교육 목적으로 제작되었습니다.

---

**즐거운 면학 생활 되세요! 📚✨**
