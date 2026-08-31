import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import json
import os
import calendar
import threading
import time
from winsound import Beep, MessageBeep
try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

# 한국 공휴일 라이브러리 (설치 필요: pip install holidays)
try:
    import holidays
    KR_HOLIDAYS = holidays.Korea()
    HOLIDAYS_AVAILABLE = True
except ImportError:
    HOLIDAYS_AVAILABLE = False
    KR_HOLIDAYS = {}

DATA_FILE = "myeonhak_data.json"
CONFIG_FILE = "myeonhak_config.json"

class MyeonhakCalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("면학 불참 계획 관리자 - Ultimate")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # 현재 날짜 설정
        self.current_date = datetime.now()
        self.selected_date = datetime.now()
        
        # 데이터 로드
        self.data = self.load_data()
        self.config = self.load_config()
        
        # 스타일 설정
        self.setup_styles()
        
        # UI 구성
        self.create_ui()
        
        # 시계 업데이트 시작
        self.update_clock()
        
        # 알람 체크 시작
        self.alarm_thread = threading.Thread(target=self.check_alarms, daemon=True)
        self.alarm_thread.start()
        
        # 바탕화면 메모 동기화 시작 (5 분마다)
        self.sync_desktop_memo()
        
    def setup_styles(self):
        """스타일 설정"""
        self.colors = {
            'bg': '#1a1a2e',
            'fg': '#eee',
            'accent': '#4ecca3',
            'danger': '#e74c3c',
            'warning': '#f1c40f',
            'info': '#3498db',
            'success': '#2ecc71',
            'card_bg': '#16213e',
            'hover': '#0f3460',
            '8면': '#e74c3c',
            '1 면': '#4ecca3',
            '2 면': '#f1c40f'
        }
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 커스텀 스타일 정의
        self.style.configure('TFrame', background=self.colors['bg'])
        self.style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'], font=('Malgun Gothic', 10))
        self.style.configure('Title.TLabel', font=('Malgun Gothic', 16, 'bold'), foreground=self.colors['accent'])
        self.style.configure('Clock.TLabel', font=('Consolas', 14, 'bold'), foreground=self.colors['accent'])
        self.style.configure('Header.TLabel', font=('Malgun Gothic', 12, 'bold'))
        self.style.configure('Card.TFrame', background=self.colors['card_bg'])
        
        self.style.configure('TButton', 
                            background=self.colors['accent'], 
                            foreground='#000', 
                            font=('Malgun Gothic', 10, 'bold'),
                            padding=5)
        self.style.map('TButton', background=[('active', self.colors['hover'])})
        
        self.style.configure('TCheckbutton', 
                            background=self.colors['bg'], 
                            foreground=self.colors['fg'],
                            font=('Malgun Gothic', 10))
        
    def create_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 상단 헤더 (시계 포함)
        header_frame = ttk.Frame(main_frame, style='TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="📅 면학 불참 계획 관리자", style='Title.TLabel')
        title_label.pack(side=tk.LEFT)
        
        self.clock_label = ttk.Label(header_frame, text="", style='Clock.TLabel')
        self.clock_label.pack(side=tk.RIGHT)
        
        # 네비게이션 버튼
        nav_frame = ttk.Frame(main_frame, style='TFrame')
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(nav_frame, text="◀ 이전", command=self.prev_month).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="오늘", command=self.go_to_today).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="다음 ▶", command=self.next_month).pack(side=tk.LEFT, padx=2)
        
        self.month_label = ttk.Label(nav_frame, text="", style='Header.TLabel')
        self.month_label.pack(side=tk.LEFT, padx=20)
        
        # 뷰 선택 버튼 (주/월/년)
        view_frame = ttk.Frame(nav_frame, style='TFrame')
        view_frame.pack(side=tk.RIGHT)
        
        ttk.Button(view_frame, text="주", command=lambda: messagebox.showinfo("안내", "주 뷰는 준비중입니다.")).pack(side=tk.LEFT, padx=2)
        ttk.Button(view_frame, text="월", command=lambda: None).pack(side=tk.LEFT, padx=2)
        ttk.Button(view_frame, text="년", command=lambda: messagebox.showinfo("안내", "년 뷰는 준비중입니다.")).pack(side=tk.LEFT, padx=2)
        
        # 콘텐츠 영역 (양쪽 패널)
        content_frame = ttk.Frame(main_frame, style='TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 왼쪽: 달력 패널
        calendar_panel = ttk.Frame(content_frame, style='Card.TFrame', padding=10)
        calendar_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.create_calendar(calendar_panel)
        
        # 오른쪽: 상세 정보 패널
        detail_panel = ttk.Frame(content_frame, style='Card.TFrame', padding=10)
        detail_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(5, 0), width=400)
        detail_panel.pack_propagate(False)
        
        self.create_detail_panel(detail_panel)
        
        # 하단: 알림 및 설정
        bottom_frame = ttk.Frame(main_frame, style='TFrame')
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(bottom_frame, text="⏰ 알람 설정", command=self.open_alarm_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="📝 바탕화면 메모 동기화", command=self.toggle_desktop_memo).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="💾 데이터 백업", command=self.backup_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="ℹ️ 프로그램 정보", command=self.show_info).pack(side=tk.RIGHT, padx=5)
        
        # 초기 달력 렌더링
        self.render_calendar()
        
    def create_calendar(self, parent):
        """달력 생성"""
        # 요일 헤더
        days_frame = ttk.Frame(parent, style='Card.TFrame')
        days_frame.pack(fill=tk.X, pady=(0, 5))
        
        days = ['월', '화', '수', '목', '금', '토', '일']
        for i, day in enumerate(days):
            color = self.colors['danger'] if i >= 5 else self.colors['fg']
            label = ttk.Label(days_frame, text=day, font=('Malgun Gothic', 11, 'bold'), 
                            foreground=color, background=self.colors['card_bg'], width=4)
            label.pack(side=tk.LEFT, expand=True)
        
        # 날짜 그리드
        self.calendar_grid = ttk.Frame(parent, style='Card.TFrame')
        self.calendar_grid.pack(fill=tk.BOTH, expand=True)
        
    def render_calendar(self):
        """달력 렌더링"""
        # 기존 위젯 제거
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()
        
        year = self.current_date.year
        month = self.current_date.month
        
        # 월 레이블 업데이트
        self.month_label.config(text=f"{year}년 {month}월")
        
        # 첫 날과 마지막 날 계산
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1])
        
        # 시작 요일 조정 (월요일 시작)
        start_weekday = first_day.weekday()
        
        # 이전 달 날짜 (회색)
        prev_month_last_day = calendar.monthrange(year, month-1 if month > 1 else 12)[1]
        for i in range(start_weekday):
            day_num = prev_month_last_day - start_weekday + i + 1
            label = ttk.Label(self.calendar_grid, text=str(day_num), 
                            font=('Malgun Gothic', 10), foreground='#666',
                            background=self.colors['card_bg'], width=4, height=2)
            label.grid(row=0, column=i, padx=2, pady=2)
        
        # 현재 달 날짜
        current_row = 0 if start_weekday == 0 else 1
        for day in range(1, last_day.day + 1):
            current_date = datetime(year, month, day)
            weekday = current_date.weekday()
            
            # 그리드 위치 계산
            col = weekday
            if weekday == 0 and day > 1:
                current_row += 1
            
            row = current_row
            if weekday > 0:
                row = (start_weekday + day - 1) // 7
            
            # 공휴일 확인
            is_holiday = False
            holiday_name = ""
            if HOLIDAYS_AVAILABLE and current_date in KR_HOLIDAYS:
                is_holiday = True
                holiday_name = KR_HOLIDAYS.get(current_date, "")
            
            # 주말 확인
            is_weekend = weekday >= 5
            
            # 색상 결정
            if is_holiday:
                fg_color = self.colors['danger']
            elif is_weekend:
                fg_color = self.colors['danger'] if weekday == 6 else '#f39c12'
            else:
                fg_color = self.colors['fg']
            
            # 면학 일정 확인
            date_str = current_date.strftime('%Y-%m-%d')
            has_schedule = date_str in self.data.get('schedules', {})
            schedule_types = []
            if has_schedule:
                sched = self.data['schedules'][date_str]
                if sched.get('8 면'): schedule_types.append('8 면')
                if sched.get('1 면'): schedule_types.append('1 면')
                if sched.get('2 면'): schedule_types.append('2 면')
            
            # 버튼 생성
            btn_text = str(day)
            if schedule_types:
                btn_text += f"\n{','.join(schedule_types)}"
            if holiday_name:
                btn_text += f"\n({holiday_name})"
            
            btn = tk.Button(self.calendar_grid, text=btn_text, 
                          font=('Malgun Gothic', 10 if not schedule_types else 9),
                          bg=self.colors['card_bg'], fg=fg_color,
                          width=4, height=2,
                          relief=tk.FLAT, cursor='hand2')
            btn.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
            
            # 클릭 이벤트
            btn.bind('<Button-1>', lambda e, d=current_date: self.select_date(d))
            
            # 오늘 강조
            if current_date.date() == datetime.now().date():
                btn.config(bg=self.colors['accent'], fg='#000')
            
            # 그리드 가중치 설정
            self.calendar_grid.grid_rowconfigure(row, weight=1)
            self.calendar_grid.grid_columnconfigure(col, weight=1)
            
            if weekday == 6 or (weekday == 0 and day > 1):
                current_row += 1
    
    def create_detail_panel(self, parent):
        """상세 정보 패널 생성"""
        # 선택된 날짜 표시
        date_frame = ttk.Frame(parent, style='Card.TFrame')
        date_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.selected_date_label = ttk.Label(date_frame, text="", style='Title.TLabel')
        self.selected_date_label.pack()
        
        # 면학 계획 섹션
        plan_frame = ttk.LabelFrame(parent, text="📚 면학 계획", 
                                   font=('Malgun Gothic', 11, 'bold'),
                                   background=self.colors['card_bg'],
                                   foreground=self.colors['accent'])
        plan_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 8 면
        self.var_8 = tk.BooleanVar()
        cb_8 = ttk.Checkbutton(plan_frame, text="8 면 (아침)", variable=self.var_8,
                              command=self.save_current_schedule)
        cb_8.pack(anchor=tk.W, padx=10, pady=5)
        
        # 1 면
        self.var_1 = tk.BooleanVar()
        cb_1 = ttk.Checkbutton(plan_frame, text="1 면 (오전)", variable=self.var_1,
                              command=self.save_current_schedule)
        cb_1.pack(anchor=tk.W, padx=10, pady=5)
        
        # 2 면
        self.var_2 = tk.BooleanVar()
        cb_2 = ttk.Checkbutton(plan_frame, text="2 면 (오후)", variable=self.var_2,
                              command=self.save_current_schedule)
        cb_2.pack(anchor=tk.W, padx=10, pady=5)
        
        # 메모 입력
        memo_frame = ttk.LabelFrame(parent, text="📝 메모",
                                   font=('Malgun Gothic', 11, 'bold'),
                                   background=self.colors['card_bg'],
                                   foreground=self.colors['accent'])
        memo_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.memo_text = tk.Text(memo_frame, height=6, width=30,
                                bg='#0f0f23', fg=self.colors['fg'],
                                insertbackground=self.colors['fg'],
                                font=('Malgun Gothic', 10),
                                relief=tk.FLAT)
        self.memo_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Button(memo_frame, text="메모 저장", command=self.save_memo).pack(pady=5)
        
        # 할 일 목록 섹션
        todo_frame = ttk.LabelFrame(parent, text="✅ 할 일 목록",
                                   font=('Malgun Gothic', 11, 'bold'),
                                   background=self.colors['card_bg'],
                                   foreground=self.colors['accent'])
        todo_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 할 일 입력
        todo_input_frame = ttk.Frame(todo_frame, style='Card.TFrame')
        todo_input_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.todo_entry = ttk.Entry(todo_input_frame, font=('Malgun Gothic', 10))
        self.todo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.todo_entry.bind('<Return>', lambda e: self.add_todo())
        
        ttk.Button(todo_input_frame, text="추가", command=self.add_todo).pack(side=tk.RIGHT)
        
        # 할 일 목록
        self.todo_listbox = tk.Listbox(todo_frame, bg='#0f0f23', fg=self.colors['fg'],
                                      selectbackground=self.colors['accent'],
                                      selectforeground='#000',
                                      font=('Malgun Gothic', 10),
                                      relief=tk.FLAT, height=6)
        self.todo_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.todo_listbox.bind('<Double-Button-1>', self.toggle_todo_complete)
        
        # 할 일 버튼
        todo_btn_frame = ttk.Frame(todo_frame, style='Card.TFrame')
        todo_btn_frame.pack(fill=tk.X)
        
        ttk.Button(todo_btn_frame, text="삭제", command=self.delete_todo).pack(side=tk.RIGHT, padx=2)
        
        # 시험 일정 섹션
        exam_frame = ttk.LabelFrame(parent, text="📖 시험 일정",
                                   font=('Malgun Gothic', 11, 'bold'),
                                   background=self.colors['card_bg'],
                                   foreground=self.colors['accent'])
        exam_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.exam_label = ttk.Label(exam_frame, text="등록된 시험 일정 없음",
                                   background=self.colors['card_bg'],
                                   foreground=self.colors['fg'])
        self.exam_label.pack(padx=10, pady=5)
        
        ttk.Button(exam_frame, text="시험 일정 추가/수정", 
                  command=self.edit_exam_schedule).pack(pady=5)
    
    def select_date(self, date):
        """날짜 선택"""
        self.selected_date = date
        date_str = date.strftime('%Y-%m-%d')
        weekday = date.strftime('%A')
        korean_weekday = {'Monday': '월요일', 'Tuesday': '화요일', 'Wednesday': '수요일',
                         'Thursday': '목요일', 'Friday': '금요일', 'Saturday': '토요일',
                         'Sunday': '일요일'}
        
        self.selected_date_label.config(text=f"{date.year}년 {date.month}월 {date.day}일 ({korean_weekday[weekday]})")
        
        # 기존 일정 로드
        schedule = self.data.get('schedules', {}).get(date_str, {})
        self.var_8.set(schedule.get('8 면', False))
        self.var_1.set(schedule.get('1 면', False))
        self.var_2.set(schedule.get('2 면', False))
        
        # 메모 로드
        self.memo_text.delete('1.0', tk.END)
        self.memo_text.insert('1.0', schedule.get('memo', ''))
        
        # 할 일 로드
        self.load_todos(date_str)
        
        # 시험 일정 로드
        self.load_exam_schedule(date_str)
        
        # 달력 다시 렌더링 (선택 강조)
        self.render_calendar()
    
    def save_current_schedule(self):
        """현재 일정 저장"""
        date_str = self.selected_date.strftime('%Y-%m-%d')
        
        if 'schedules' not in self.data:
            self.data['schedules'] = {}
        
        self.data['schedules'][date_str] = {
            '8 면': self.var_8.get(),
            '1 면': self.var_1.get(),
            '2 면': self.var_2.get(),
            'memo': self.memo_text.get('1.0', tk.END).strip(),
            'todos': self.data.get('schedules', {}).get(date_str, {}).get('todos', []),
            'exam': self.data.get('schedules', {}).get(date_str, {}).get('exam', '')
        }
        
        self.save_data()
        self.render_calendar()
    
    def save_memo(self):
        """메모 저장"""
        self.save_current_schedule()
        messagebox.showinfo("저장 완료", "메모가 저장되었습니다.")
    
    def load_todos(self, date_str):
        """할 일 로드"""
        self.todo_listbox.delete(0, tk.END)
        todos = self.data.get('schedules', {}).get(date_str, {}).get('todos', [])
        for todo in todos:
            status = "✓" if todo.get('done', False) else "○"
            self.todo_listbox.insert(tk.END, f"{status} {todo['text']}")
    
    def add_todo(self):
        """할 일 추가"""
        text = self.todo_entry.get().strip()
        if not text:
            return
        
        date_str = self.selected_date.strftime('%Y-%m-%d')
        if 'schedules' not in self.data:
            self.data['schedules'] = {}
        if date_str not in self.data['schedules']:
            self.data['schedules'][date_str] = {'todos': []}
        
        self.data['schedules'][date_str]['todos'].append({'text': text, 'done': False})
        self.todo_entry.delete(0, tk.END)
        self.save_data()
        self.load_todos(date_str)
    
    def toggle_todo_complete(self, event):
        """할 일 완료 토글"""
        selection = self.todo_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        date_str = self.selected_date.strftime('%Y-%m-%d')
        todos = self.data.get('schedules', {}).get(date_str, {}).get('todos', [])
        
        if index < len(todos):
            todos[index]['done'] = not todos[index]['done']
            self.save_data()
            self.load_todos(date_str)
    
    def delete_todo(self):
        """할 일 삭제"""
        selection = self.todo_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        date_str = self.selected_date.strftime('%Y-%m-%d')
        todos = self.data.get('schedules', {}).get(date_str, {}).get('todos', [])
        
        if index < len(todos):
            del todos[index]
            self.save_data()
            self.load_todos(date_str)
    
    def load_exam_schedule(self, date_str):
        """시험 일정 로드"""
        exam = self.data.get('schedules', {}).get(date_str, {}).get('exam', '')
        if exam:
            self.exam_label.config(text=f"📖 {exam}")
        else:
            self.exam_label.config(text="등록된 시험 일정 없음")
    
    def edit_exam_schedule(self):
        """시험 일정 편집"""
        date_str = self.selected_date.strftime('%Y-%m-%d')
        current_exam = self.data.get('schedules', {}).get(date_str, {}).get('exam', '')
        
        exam = simpledialog.askstring("시험 일정", "시험 과목 및 내용을 입력하세요:", initialvalue=current_exam)
        
        if exam is not None:
            if 'schedules' not in self.data:
                self.data['schedules'] = {}
            if date_str not in self.data['schedules']:
                self.data['schedules'][date_str] = {}
            
            self.data['schedules'][date_str]['exam'] = exam
            self.save_data()
            self.load_exam_schedule(date_str)
    
    def update_clock(self):
        """시계 업데이트"""
        now = datetime.now()
        self.clock_label.config(text=now.strftime('%Y-%m-%d %H:%M:%S'))
        self.root.after(1000, self.update_clock)
    
    def check_alarms(self):
        """알람 체크 (백그라운드)"""
        while True:
            time.sleep(30)  # 30 초마다 체크
            now = datetime.now()
            current_time = now.strftime('%H:%M')
            current_date = now.strftime('%Y-%m-%d')
            
            alarms = self.config.get('alarms', [])
            for alarm in alarms:
                if alarm.get('enabled', True) and alarm.get('time') == current_time:
                    if alarm.get('date') == current_date or not alarm.get('date'):
                        self.root.after(0, lambda a=alarm: self.trigger_alarm(a))
    
    def trigger_alarm(self, alarm):
        """알람 발생"""
        message = f"⏰ 알람!\n\n{alarm.get('message', '예약된 시간입니다.')}"
        
        if SOUND_AVAILABLE:
            try:
                Beep(1000, 500)  # 1kHz, 0.5 초
                MessageBeep()
            except:
                pass
        
        messagebox.showwarning("알람", message)
    
    def open_alarm_settings(self):
        """알람 설정 창"""
        alarm_win = tk.Toplevel(self.root)
        alarm_win.title("알람 설정")
        alarm_win.geometry("400x300")
        alarm_win.configure(bg=self.colors['bg'])
        
        ttk.Label(alarm_win, text="⏰ 알람 설정", style='Title.TLabel').pack(pady=10)
        
        # 알람 목록
        list_frame = ttk.Frame(alarm_win, style='Card.TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        alarm_listbox = tk.Listbox(list_frame, bg='#0f0f23', fg=self.colors['fg'],
                                  font=('Malgun Gothic', 10))
        alarm_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        alarms = self.config.get('alarms', [])
        for alarm in alarms:
            alarm_listbox.insert(tk.END, f"{alarm['time']} - {alarm.get('message', '알람')}")
        
        # 버튼
        btn_frame = ttk.Frame(alarm_win, style='TFrame')
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def add_alarm():
            time_str = simpledialog.askstring("시간", "알람 시간을 입력하세요 (HH:MM 형식):")
            if not time_str:
                return
            msg = simpledialog.askstring("메시지", "알람 메시지를 입력하세요:")
            
            new_alarm = {'time': time_str, 'message': msg or '알람', 'enabled': True}
            if 'alarms' not in self.config:
                self.config['alarms'] = []
            self.config['alarms'].append(new_alarm)
            self.save_config()
            
            alarm_listbox.insert(tk.END, f"{time_str} - {msg or '알람'}")
        
        ttk.Button(btn_frame, text="추가", command=add_alarm).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="닫기", command=alarm_win.destroy).pack(side=tk.RIGHT, padx=5)
    
    def sync_desktop_memo(self):
        """바탕화면 메모 동기화"""
        # 간단한 구현: 데이터를 텍스트 파일로 내보내기
        memo_file = os.path.join(os.path.expanduser('~'), 'Desktop', '면학_메모.txt')
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            schedule = self.data.get('schedules', {}).get(today, {})
            
            with open(memo_file, 'w', encoding='utf-8') as f:
                f.write(f"=== 면학 계획 ({today}) ===\n\n")
                f.write(f"8 면: {'✓' if schedule.get('8 면') else '○'}\n")
                f.write(f"1 면: {'✓' if schedule.get('1 면') else '○'}\n")
                f.write(f"2 면: {'✓' if schedule.get('2 면') else '○'}\n\n")
                f.write(f"메모:\n{schedule.get('memo', '없음')}\n\n")
                f.write("할 일:\n")
                for todo in schedule.get('todos', []):
                    status = "✓" if todo.get('done') else "○"
                    f.write(f"  {status} {todo['text']}\n")
            
            print(f"바탕화면 메모 동기화 완료: {memo_file}")
        except Exception as e:
            print(f"바탕화면 동기화 오류: {e}")
    
    def toggle_desktop_memo(self):
        """바탕화면 메모 동기화 토글"""
        self.sync_desktop_memo()
        messagebox.showinfo("동기화 완료", "바탕화면에 '면학_메모.txt' 파일이 생성/업데이트되었습니다.")
    
    def backup_data(self):
        """데이터 백업"""
        backup_file = f"myeonhak_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("백업 완료", f"데이터가 백업되었습니다:\n{backup_file}")
        except Exception as e:
            messagebox.showerror("백업 오류", f"백업 중 오류가 발생했습니다:\n{str(e)}")
    
    def show_info(self):
        """프로그램 정보"""
        info = """
📅 면학 불참 계획 관리자 - Ultimate Edition

기능:
• 월간 달력 뷰에서 면학 계획 관리
• 8 면/1 면/2 면 불참·참가 설정
• 날짜별 할 일 목록 관리
• 시험 일정 등록
• 한국 공휴일 자동 표시
• 실시간 시계 동기화
• 알람 기능
• 바탕화면 메모 동기화
• 자동 데이터 저장

버전: 3.0 Ultimate
"""
        messagebox.showinfo("프로그램 정보", info)
    
    def prev_month(self):
        """이전 달"""
        if self.current_date.month == 1:
            self.current_date = datetime(self.current_date.year - 1, 12, 1)
        else:
            self.current_date = datetime(self.current_date.year, self.current_date.month - 1, 1)
        self.render_calendar()
    
    def next_month(self):
        """다음 달"""
        if self.current_date.month == 12:
            self.current_date = datetime(self.current_date.year + 1, 1, 1)
        else:
            self.current_date = datetime(self.current_date.year, self.current_date.month + 1, 1)
        self.render_calendar()
    
    def go_to_today(self):
        """오늘로 이동"""
        self.current_date = datetime.now()
        self.selected_date = datetime.now()
        self.render_calendar()
        self.select_date(self.selected_date)
    
    def load_data(self):
        """데이터 로드"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {'schedules': {}}
    
    def save_data(self):
        """데이터 저장"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def load_config(self):
        """설정 로드"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {'alarms': []}
    
    def save_config(self):
        """설정 저장"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = MyeonhakCalendarApp(root)
    root.mainloop()
