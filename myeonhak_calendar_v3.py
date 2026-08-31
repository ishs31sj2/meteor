import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import json
import os
import calendar
import holidays  # 한국 공휴일 지원을 위한 라이브러리

# 데이터 파일 경로
DATA_FILE = "myeonhak_data.json"

class MyeonhakCalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("면학 불참 계획 관리자 (실시간/공휴일 지원)")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        
        # 테마 설정 (다크 모드 스타일)
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'panel_bg': '#2d2d2d',
            'accent': '#4CAF50',
            'highlight': '#ff9800',
            'weekend': '#ff5252',
            '8myeon': '#ff4444',  # 빨강
            '1myeon': '#00e5ff',  # 민트
            '2myeon': '#ffea00',  # 노랑
            'holiday': '#ff8a80'  # 공휴일 색상
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # 데이터 로드
        self.data = self.load_data()
        self.current_date = datetime.now()
        self.selected_date = datetime.now()
        
        # 한국 공휴일 객체 생성 (자동 업데이트됨)
        self.kr_holidays = holidays.KR()
        
        # UI 구성
        self.setup_ui()
        
        # 실시간 시계 업데이트 시작
        self.update_clock()
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 왼쪽: 달력 패널
        left_panel = tk.Frame(main_frame, bg=self.colors['panel_bg'], width=600)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # 상단 컨트롤 (연/월 선택 및 오늘 버튼)
        control_frame = tk.Frame(left_panel, bg=self.colors['panel_bg'])
        control_frame.pack(fill=tk.X, pady=10)
        
        self.lbl_year_month = tk.Label(control_frame, text="", font=("Helvetica", 16, "bold"), 
                                       bg=self.colors['panel_bg'], fg=self.colors['fg'])
        self.lbl_year_month.pack(side=tk.LEFT, padx=20)
        
        btn_prev = tk.Button(control_frame, text="<", command=self.prev_month, 
                            bg=self.colors['panel_bg'], fg=self.colors['fg'], bd=0, font=("Arial", 12))
        btn_prev.pack(side=tk.LEFT)
        
        btn_next = tk.Button(control_frame, text=">", command=self.next_month, 
                            bg=self.colors['panel_bg'], fg=self.colors['fg'], bd=0, font=("Arial", 12))
        btn_next.pack(side=tk.LEFT)
        
        btn_today = tk.Button(control_frame, text="오늘", command=self.go_to_today, 
                             bg=self.colors['accent'], fg="white", bd=0, padx=10, font=("Arial", 10, "bold"))
        btn_today.pack(side=tk.RIGHT, padx=10)
        
        # 실시간 시계 표시
        self.lbl_clock = tk.Label(control_frame, text="", font=("Courier", 12, "bold"), 
                                  bg=self.colors['panel_bg'], fg=self.colors['highlight'])
        self.lbl_clock.pack(side=tk.RIGHT, padx=10)
        
        # 요일 헤더
        days_header = ["월", "화", "수", "목", "금", "토", "일"]
        header_frame = tk.Frame(left_panel, bg=self.colors['panel_bg'])
        header_frame.pack(fill=tk.X, padx=20)
        for i, day in enumerate(days_header):
            color = self.colors['weekend'] if i >= 5 else self.colors['fg']
            lbl = tk.Label(header_frame, text=day, width=10, height=2, 
                          bg=self.colors['panel_bg'], fg=color, font=("Arial", 10, "bold"))
            lbl.pack(side=tk.LEFT, expand=True)
            
        # 달력 그리드
        self.calendar_frame = tk.Frame(left_panel, bg=self.colors['panel_bg'])
        self.calendar_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.draw_calendar()
        
        # 오른쪽: 상세 정보 패널
        right_panel = tk.Frame(main_frame, bg=self.colors['panel_bg'], width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # 선택된 날짜 표시
        self.lbl_selected_date = tk.Label(right_panel, text="", font=("Helvetica", 14, "bold"), 
                                         bg=self.colors['panel_bg'], fg=self.colors['accent'])
        self.lbl_selected_date.pack(pady=20)
        
        # 공휴일 알림 라벨
        self.lbl_holiday = tk.Label(right_panel, text="", font=("Arial", 10), 
                                   bg=self.colors['panel_bg'], fg=self.colors['holiday'])
        self.lbl_holiday.pack(pady=(0, 10))
        
        # 면학 계획 프레임
        plan_frame = tk.LabelFrame(right_panel, text="📚 면학 계획 (8 면/1 면/2 면)", 
                                  bg=self.colors['panel_bg'], fg=self.colors['fg'], font=("Arial", 11, "bold"))
        plan_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.myeon_vars = {}
        myeon_types = [("8 면", "8myeon"), ("1 면", "1myeon"), ("2 면", "2myeon")]
        
        for name, key in myeon_types:
            frame = tk.Frame(plan_frame, bg=self.colors['panel_bg'])
            frame.pack(fill=tk.X, pady=5)
            
            var = tk.BooleanVar(value=False)
            self.myeon_vars[key] = var
            
            chk = tk.Checkbutton(frame, variable=var, command=self.save_data, 
                                bg=self.colors['panel_bg'], activebackground=self.colors['panel_bg'],
                                selectcolor=self.colors['bg'], fg=self.colors['fg'], 
                                font=("Arial", 11))
            chk.pack(side=tk.LEFT)
            
            lbl = tk.Label(frame, text=name, bg=self.colors['panel_bg'], fg=self.colors['fg'], font=("Arial", 11))
            lbl.pack(side=tk.LEFT, padx=5)
            
            # 색상 인디케이터
            color_map = {"8myeon": self.colors['8myeon'], "1myeon": self.colors['1myeon'], "2myeon": self.colors['2myeon']}
            indicator = tk.Label(frame, text="●", fg=color_map[key], bg=self.colors['panel_bg'], font=("Arial", 12))
            indicator.pack(side=tk.RIGHT)
            
        # 메모 입력
        memo_label = tk.Label(plan_frame, text="메모:", bg=self.colors['panel_bg'], fg=self.colors['fg'], font=("Arial", 10))
        memo_label.pack(anchor=tk.W, padx=5, pady=(10, 0))
        
        self.memo_entry = tk.Text(plan_frame, height=4, bg="#3d3d3d", fg="white", 
                                 insertbackground="white", font=("Arial", 10), bd=0)
        self.memo_entry.pack(fill=tk.X, padx=5, pady=5)
        self.memo_entry.bind("<KeyRelease>", lambda e: self.save_data())
        
        # 할 일 목록
        todo_frame = tk.LabelFrame(right_panel, text="✅ 할 일 목록", 
                                  bg=self.colors['panel_bg'], fg=self.colors['fg'], font=("Arial", 11, "bold"))
        todo_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 할 일 입력
        input_frame = tk.Frame(todo_frame, bg=self.colors['panel_bg'])
        input_frame.pack(fill=tk.X, pady=5)
        
        self.todo_entry = tk.Entry(input_frame, bg="#3d3d3d", fg="white", 
                                  insertbackground="white", font=("Arial", 10), bd=0)
        self.todo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.todo_entry.bind("<Return>", lambda e: self.add_todo())
        
        btn_add = tk.Button(input_frame, text="+", command=self.add_todo, 
                           bg=self.colors['accent'], fg="white", bd=0, font=("Arial", 12, "bold"), width=3)
        btn_add.pack(side=tk.RIGHT)
        
        # 할 일 리스트박스
        self.todo_listbox = tk.Listbox(todo_frame, bg="#3d3d3d", fg="white", 
                                      selectbackground=self.colors['highlight'], 
                                      selectforeground="black", font=("Arial", 10), bd=0, height=8)
        self.todo_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.todo_listbox.bind("<Double-Button-1>", self.toggle_todo_complete)
        
        # 할 일 삭제 버튼
        btn_del_todo = tk.Button(todo_frame, text="선택 항목 삭제", command=self.delete_todo, 
                                bg="#ff5252", fg="white", bd=0, font=("Arial", 9))
        btn_del_todo.pack(fill=tk.X, pady=5)
        
        # 초기 화면 렌더링
        self.update_display()

    def draw_calendar(self):
        # 기존 위젯 제거
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
            
        year = self.current_date.year
        month = self.current_date.month
        
        # 달력 데이터 생성
        cal = calendar.monthcalendar(year, month)
        
        for week_idx, week in enumerate(cal):
            for day_idx, day in enumerate(week):
                if day == 0:
                    continue
                    
                # 날짜 프레임
                day_frame = tk.Frame(self.calendar_frame, bg=self.colors['panel_bg'], highlightthickness=1, highlightbackground="#444")
                day_frame.grid(row=week_idx+1, column=day_idx, sticky="nsew", padx=2, pady=2)
                self.calendar_frame.grid_rowconfigure(week_idx+1, weight=1)
                self.calendar_frame.grid_columnconfigure(day_idx, weight=1)
                
                # 실제 날짜 객체
                current_day = datetime(year, month, day)
                date_str = current_day.strftime("%Y-%m-%d")
                
                # 요일 색상 (주말)
                is_weekend = day_idx >= 5
                fg_color = self.colors['weekend'] if is_weekend else self.colors['fg']
                
                # 공휴일 체크
                is_holiday = date_str in self.kr_holidays
                holiday_name = self.kr_holidays.get(date_str)
                if is_holiday:
                    fg_color = self.colors['holiday']
                
                # 오늘 날짜 강조
                is_today = current_day.date() == datetime.now().date()
                bg_color = "#444" if is_today else self.colors['panel_bg']
                if is_today:
                    fg_color = self.colors['accent']
                
                # 선택된 날짜 강조
                if current_day.date() == self.selected_date.date():
                    bg_color = "#555"
                    day_frame.config(highlightbackground=self.colors['accent'], highlightthickness=2)
                
                # 면학 계획 인디케이터
                indicators = ""
                if date_str in self.data:
                    day_data = self.data[date_str]
                    if day_data.get('8myeon'): indicators += "🔴"
                    if day_data.get('1myeon'): indicators += "🔵"
                    if day_data.get('2myeon'): indicators += "🟡"
                
                # 날짜 라벨
                lbl_date = tk.Label(day_frame, text=str(day), bg=bg_color, fg=fg_color, 
                                   font=("Arial", 12, "bold" if is_today else "normal"))
                lbl_date.pack(anchor=tk.NW, padx=5, pady=2)
                
                # 공휴일 이름 라벨 (작은 글씨)
                if is_holiday:
                    lbl_hol = tk.Label(day_frame, text=holiday_name[:3], bg=bg_color, fg=fg_color, 
                                      font=("Arial", 7))
                    lbl_hol.pack(anchor=tk.NW, padx=5)
                
                # 면학 인디케이터
                if indicators:
                    lbl_ind = tk.Label(day_frame, text=indicators, bg=bg_color, fg=fg_color, 
                                      font=("Arial", 8))
                    lbl_ind.pack(anchor=tk.SW, padx=5, pady=2)
                
                # 클릭 이벤트
                day_frame.bind("<Button-1>", lambda e, d=current_day: self.select_date(d))
                lbl_date.bind("<Button-1>", lambda e, d=current_day: self.select_date(d))
                if is_holiday:
                    lbl_hol.bind("<Button-1>", lambda e, d=current_day: self.select_date(d))
                if indicators:
                    lbl_ind.bind("<Button-1>", lambda e, d=current_day: self.select_date(d))

    def select_date(self, date_obj):
        self.selected_date = date_obj
        self.draw_calendar()  # 선택 시각화 업데이트
        self.update_display()
        
    def update_display(self):
        # 연/월 표시
        self.lbl_year_month.config(text=f"{self.current_date.year}년 {self.current_date.month}월")
        
        # 선택된 날짜 표시
        date_str = self.selected_date.strftime("%Y-%m-%d")
        day_name = ["월", "화", "수", "목", "금", "토", "일"][self.selected_date.weekday()]
        self.lbl_selected_date.config(text=f"{date_str} ({day_name}요일)")
        
        # 공휴일 표시
        if date_str in self.kr_holidays:
            self.lbl_holiday.config(text=f"🎉 공휴일: {self.kr_holidays.get(date_str)}")
        else:
            self.lbl_holiday.config(text="")
        
        # 면학 계획 로드
        day_data = self.data.get(date_str, {})
        for key in self.myeon_vars:
            self.myeon_vars[key].set(day_data.get(key, False))
            
        # 메모 로드
        self.memo_entry.delete("1.0", tk.END)
        self.memo_entry.insert(tk.END, day_data.get('memo', ''))
        
        # 할 일 로드
        self.todo_listbox.delete(0, tk.END)
        todos = day_data.get('todos', [])
        for todo in todos:
            prefix = "[완료] " if todo.get('done') else ""
            self.todo_listbox.insert(tk.END, f"{prefix}{todo['text']}")
            
    def prev_month(self):
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year-1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month-1)
        self.draw_calendar()
        
    def next_month(self):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year+1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month+1)
        self.draw_calendar()
        
    def go_to_today(self):
        self.current_date = datetime.now()
        self.selected_date = datetime.now()
        self.draw_calendar()
        self.update_display()
        
    def update_clock(self):
        now = datetime.now()
        self.lbl_clock.config(text=now.strftime("%H:%M:%S"))
        # 매초 업데이트
        self.root.after(1000, self.update_clock)
        
    def add_todo(self):
        text = self.todo_entry.get().strip()
        if not text:
            return
            
        date_str = self.selected_date.strftime("%Y-%m-%d")
        if date_str not in self.data:
            self.data[date_str] = {'todos': []}
        if 'todos' not in self.data[date_str]:
            self.data[date_str]['todos'] = []
            
        self.data[date_str]['todos'].append({'text': text, 'done': False})
        self.todo_entry.delete(0, tk.END)
        self.save_data()
        self.update_display()
        
    def toggle_todo_complete(self, event):
        selection = self.todo_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        date_str = self.selected_date.strftime("%Y-%m-%d")
        
        if date_str in self.data and index < len(self.data[date_str].get('todos', [])):
            todo = self.data[date_str]['todos'][index]
            todo['done'] = not todo['done']
            self.save_data()
            self.update_display()
            
    def delete_todo(self):
        selection = self.todo_listbox.curselection()
        if not selection:
            messagebox.showwarning("알림", "삭제할 할 일을 선택해주세요.")
            return
            
        index = selection[0]
        date_str = self.selected_date.strftime("%Y-%m-%d")
        
        if date_str in self.data and index < len(self.data[date_str].get('todos', [])):
            del self.data[date_str]['todos'][index]
            self.save_data()
            self.update_display()
            
    def save_data(self):
        date_str = self.selected_date.strftime("%Y-%m-%d")
        
        # 면학 상태 저장
        myeon_status = {key: var.get() for key, var in self.myeon_vars.items()}
        
        # 메모 저장
        memo = self.memo_entry.get("1.0", tk.END).strip()
        
        # 기존 데이터 유지 (할 일 등)
        if date_str not in self.data:
            self.data[date_str] = {}
            
        self.data[date_str].update(myeon_status)
        self.data[date_str]['memo'] = memo
        
        # JSON 저장
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("오류", f"데이터 저장 중 오류 발생: {str(e)}")
            
    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return {}
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

if __name__ == "__main__":
    root = tk.Tk()
    app = MyeonhakCalendarApp(root)
    root.mainloop()
