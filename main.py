import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import datetime
import calendar
import holidays
import threading
import winsound
from datetime import datetime as dt

# 데이터 파일 경로
DATA_FILE = "myeonhak_data.json"
DESKTOP_MEMO_FILE = "면학_바탕화면_메모.txt"

class MyeonhakManager:
    def __init__(self, root):
        self.root = root
        self.root.title("면학 불참 계획 관리자 v5 (Ultimate)")
        self.root.geometry("1000x700")
        self.root.minsize(900, 650)
        
        # 테마 설정 (다크 모드 스타일)
        self.colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'accent': '#4a90e2',
            'panel': '#3c3f41',
            'entry_bg': '#454545',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'type_8': '#ff5252',  # 8면 빨강
            'type_1': '#69f0ae',  # 1면 민트
            'type_2': '#ffd740'   # 2면 노랑
        }
        
        self.root.configure(bg=self.colors['bg'])
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", background=self.colors['accent'], foreground='white', borderwidth=0, focusthickness=0, font=('Malgun Gothic', 10))
        style.map("TButton", background=[('active', '#357abd')])
        style.configure("TLabel", background=self.colors['bg'], foreground=self.colors['fg'], font=('Malgun Gothic', 10))
        style.configure("Title.TLabel", font=('Malgun Gothic', 16, 'bold'))
        style.configure("Treeview", background=self.colors['panel'], foreground=self.colors['fg'], fieldbackground=self.colors['panel'], rowheight=25, font=('Malgun Gothic', 10))
        style.configure("Treeview.Heading", background=self.colors['panel'], foreground=self.colors['accent'], font=('Malgun Gothic', 10, 'bold'))
        style.map("Treeview", background=[('selected', self.colors['accent'])])

        # 데이터 로드
        self.data = self.load_data()
        self.current_date = dt.now()
        self.selected_date = dt.now().date()
        self.ko_holidays = holidays.KR()

        # UI 레이아웃
        self.create_ui()
        
        # 시계 업데이트 시작
        self.update_clock()
        
        # 알람 체크 스레드
        self.alarm_thread = threading.Thread(target=self.check_alarms, daemon=True)
        self.alarm_thread.start()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {'schedules': {}, 'todos': {}, 'alarms': []}

    def save_data(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
        self.sync_desktop_memo()

    def create_ui(self):
        # 상단 프레임 (시계 + 제목)
        top_frame = tk.Frame(self.root, bg=self.colors['panel'], height=60)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        top_frame.pack_propagate(False)
        
        title_label = tk.Label(top_frame, text="📅 면학 불참 계획 관리자", font=('Malgun Gothic', 18, 'bold'), bg=self.colors['panel'], fg=self.colors['accent'])
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        self.clock_label = tk.Label(top_frame, text="", font=('Consolas', 16, 'bold'), bg=self.colors['panel'], fg=self.colors['fg'])
        self.clock_label.pack(side=tk.RIGHT, padx=20, pady=15)

        # 메인 컨테이너
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 왼쪽: 달력 패널
        left_panel = tk.Frame(main_container, bg=self.colors['panel'], width=450)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        self.create_calendar(left_panel)

        # 오른쪽: 정보 및 할 일 패널
        right_panel = tk.Frame(main_container, bg=self.colors['bg'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_info_panel(right_panel)

    def create_calendar(self, parent):
        # 년/월 선택
        nav_frame = tk.Frame(parent, bg=self.colors['panel'])
        nav_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(nav_frame, text="<", command=self.prev_month, bg=self.colors['panel'], fg=self.colors['fg'], font=('Malgun Gothic', 12, 'bold'), bd=0).pack(side=tk.LEFT, padx=10)
        self.month_label = tk.Label(nav_frame, text="", font=('Malgun Gothic', 14, 'bold'), bg=self.colors['panel'], fg=self.colors['accent'])
        self.month_label.pack(side=tk.LEFT, expand=True)
        tk.Button(nav_frame, text=">", command=self.next_month, bg=self.colors['panel'], fg=self.colors['fg'], font=('Malgun Gothic', 12, 'bold'), bd=0).pack(side=tk.RIGHT, padx=10)
        tk.Button(nav_frame, text="오늘", command=self.go_today, bg=self.colors['accent'], fg='white', font=('Malgun Gothic', 10), bd=0, padx=10).pack(side=tk.RIGHT, padx=5)

        # 요일 헤더
        days_frame = tk.Frame(parent, bg=self.colors['panel'])
        days_frame.pack(fill=tk.X, padx=5)
        days = ["월", "화", "수", "목", "금", "토", "일"]
        for i, day in enumerate(days):
            color = '#ff5252' if i >= 5 else self.colors['fg']
            lbl = tk.Label(days_frame, text=day, bg=self.colors['panel'], fg=color, font=('Malgun Gothic', 10, 'bold'), width=4)
            lbl.pack(side=tk.LEFT, expand=True)

        # 날짜 그리드
        self.calendar_frame = tk.Frame(parent, bg=self.colors['panel'])
        self.calendar_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.render_calendar()

    def render_calendar(self):
        # 기존 위젯 제거
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
            
        year = self.current_date.year
        month = self.current_date.month
        self.month_label.config(text=f"{year}년 {month}월")
        
        cal = calendar.monthcalendar(year, month)
        
        rows = len(cal)
        cols = 7
        
        for r in range(rows):
            for c in range(cols):
                day = cal[r][c]
                frame = tk.Frame(self.calendar_frame, bg=self.colors['panel'], highlightthickness=1, highlightbackground='#555')
                frame.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                self.calendar_frame.grid_rowconfigure(r, weight=1)
                self.calendar_frame.grid_columnconfigure(c, weight=1)
                
                if day == 0:
                    continue
                
                date_obj = dt(year, month, day).date()
                date_str = date_obj.isoformat()
                
                is_weekend = c >= 5
                is_holiday = date_obj in self.ko_holidays
                holiday_name = self.ko_holidays.get(date_obj, "")
                
                fg_color = '#ff5252' if (is_weekend or is_holiday) else self.colors['fg']
                bg_color = self.colors['panel']
                
                # 선택된 날짜 강조
                if date_obj == self.selected_date:
                    bg_color = self.colors['accent']
                    fg_color = 'white'
                
                # 면학 표시 인디케이터
                has_plan = False
                plan_type = None
                if date_str in self.data['schedules']:
                    s = self.data['schedules'][date_str]
                    if s.get('type'):
                        has_plan = True
                        plan_type = s['type']
                
                btn = tk.Button(frame, text=str(day), bg=bg_color, fg=fg_color, 
                                font=('Malgun Gothic', 11, 'bold' if date_obj==self.selected_date else 'normal'),
                                bd=0, command=lambda d=day: self.select_date(d))
                btn.pack(expand=True, fill=tk.BOTH)
                
                if has_plan:
                    indicator = tk.Label(frame, text="●", bg=bg_color, 
                                         fg=self.colors[f'type_{plan_type}'] if plan_type in ['8','1','2'] else self.colors['accent'],
                                         font=('Arial', 8))
                    indicator.place(relx=0.5, rely=0.8, anchor=tk.CENTER)
                
                if is_holiday and holiday_name:
                    hol_lbl = tk.Label(frame, text=holiday_name[:3], bg=bg_color, fg='#ff5252', font=('Malgun Gothic', 7))
                    hol_lbl.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

    def select_date(self, day):
        self.selected_date = dt(self.current_date.year, self.current_date.month, day).date()
        self.render_calendar()
        self.refresh_info_panel()

    def prev_month(self):
        prev = self.current_date.replace(day=1) - datetime.timedelta(days=1)
        self.current_date = prev.replace(day=1)
        self.render_calendar()

    def next_month(self):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year+1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month+1)
        self.render_calendar()

    def go_today(self):
        self.current_date = dt.now()
        self.selected_date = dt.now().date()
        self.render_calendar()
        self.refresh_info_panel()

    def create_info_panel(self, parent):
        # 상단: 날짜 및 면학 설정
        top_frame = tk.LabelFrame(parent, text="📝 면학 계획 설정", bg=self.colors['panel'], fg=self.colors['fg'], font=('Malgun Gothic', 12, 'bold'))
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_date_label = tk.Label(top_frame, text="", font=('Malgun Gothic', 14, 'bold'), bg=self.colors['panel'], fg=self.colors['accent'])
        self.info_date_label.pack(pady=5)
        
        # 면학 타입 선택
        type_frame = tk.Frame(top_frame, bg=self.colors['panel'])
        type_frame.pack(pady=5)
        
        self.var_type = tk.StringVar(value="none")
        types = [("8면 (취침)", "8"), ("1면 (아침)", "1"), ("2면 (점심)", "2"), ("정상 참석", "none")]
        for txt, val in types:
            rb = tk.Radiobutton(type_frame, text=txt, variable=self.var_type, value=val, 
                                bg=self.colors['panel'], fg=self.colors['fg'], selectcolor=self.colors['bg'],
                                command=self.save_schedule)
            rb.pack(side=tk.LEFT, padx=10)
            
        # 면불 사유 입력
        reason_frame = tk.Frame(top_frame, bg=self.colors['panel'])
        reason_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(reason_frame, text="면불 사유:", bg=self.colors['panel'], fg=self.colors['fg']).pack(side=tk.LEFT)
        self.reason_entry = tk.Entry(reason_frame, bg=self.colors['entry_bg'], fg=self.colors['fg'], insertbackground='white')
        self.reason_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.reason_entry.bind('<KeyRelease>', lambda e: self.save_schedule())

        # 중간: 할 일 (ToDo) 관리
        mid_frame = tk.LabelFrame(parent, text="✅ 할 일 (ToDo) 관리", bg=self.colors['panel'], fg=self.colors['fg'], font=('Malgun Gothic', 12, 'bold'))
        mid_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 할 일 입력
        todo_input_frame = tk.Frame(mid_frame, bg=self.colors['panel'])
        todo_input_frame.pack(fill=tk.X, padx=5, pady=5)
        self.todo_entry = tk.Entry(todo_input_frame, bg=self.colors['entry_bg'], fg=self.colors['fg'], insertbackground='white')
        self.todo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.todo_entry.bind('<Return>', lambda e: self.add_todo())
        tk.Button(todo_input_frame, text="추가", command=self.add_todo, bg=self.colors['success'], fg='white').pack(side=tk.LEFT, padx=5)
        
        # 할 일 목록
        columns = ('done', 'task')
        self.todo_tree = ttk.Treeview(mid_frame, columns=columns, show='headings', height=8)
        self.todo_tree.heading('done', text='완료', anchor=tk.CENTER)
        self.todo_tree.heading('task', text='할 일 내용')
        self.todo_tree.column('done', width=50, anchor=tk.CENTER)
        self.todo_tree.column('task', width=400)
        self.todo_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.todo_tree.bind('<Double-1>', self.toggle_todo)
        
        # 할 일 버튼
        todo_btn_frame = tk.Frame(mid_frame, bg=self.colors['panel'])
        todo_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(todo_btn_frame, text="삭제", command=self.delete_todo, bg=self.colors['danger'], fg='white').pack(side=tk.RIGHT)

        # 하단: 유틸리티
        bottom_frame = tk.Frame(parent, bg=self.colors['bg'])
        bottom_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(bottom_frame, text="⏰ 알람 설정", command=self.set_alarm, bg=self.colors['warning'], fg='black').pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="📝 바탕화면 메모 동기화", command=self.sync_desktop_memo, bg=self.colors['accent'], fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="💾 데이터 백업", command=self.backup_data, bg='#607d8b', fg='white').pack(side=tk.RIGHT, padx=5)

    def refresh_info_panel(self):
        date_str = self.selected_date.isoformat()
        weekday = ["월", "화", "수", "목", "금", "토", "일"][self.selected_date.weekday()]
        self.info_date_label.config(text=f"{self.selected_date.year}년 {self.selected_date.month}월 {self.selected_date.day}일 ({weekday}요일)")
        
        # 면학 정보 로드
        schedule = self.data['schedules'].get(date_str, {})
        self.var_type.set(schedule.get('type', 'none'))
        self.reason_entry.delete(0, tk.END)
        self.reason_entry.insert(0, schedule.get('reason', ''))
        
        # 할 일 로드
        for item in self.todo_tree.get_children():
            self.todo_tree.delete(item)
        
        todos = self.data['todos'].get(date_str, [])
        for todo in todos:
            status = "✓" if todo['done'] else ""
            self.todo_tree.insert('', tk.END, values=(status, todo['text']), tags=('done' if todo['done'] else 'active'))
        
        self.todo_tree.tag_configure('done', foreground='#4caf50')
        self.todo_tree.tag_configure('active', foreground=self.colors['fg'])

    def save_schedule(self):
        date_str = self.selected_date.isoformat()
        if date_str not in self.data['schedules']:
            self.data['schedules'][date_str] = {}
        
        self.data['schedules'][date_str]['type'] = self.var_type.get()
        self.data['schedules'][date_str]['reason'] = self.reason_entry.get()
        self.data['schedules'][date_str]['updated_at'] = dt.now().isoformat()
        
        self.save_data()
        self.render_calendar() # 인디케이터 업데이트

    def add_todo(self):
        text = self.todo_entry.get().strip()
        if not text:
            return
        
        date_str = self.selected_date.isoformat()
        if date_str not in self.data['todos']:
            self.data['todos'][date_str] = []
        
        self.data['todos'][date_str].append({'text': text, 'done': False})
        self.todo_entry.delete(0, tk.END)
        self.save_data()
        self.refresh_info_panel()

    def toggle_todo(self, event):
        selection = self.todo_tree.selection()
        if not selection:
            return
        item = selection[0]
        values = self.todo_tree.item(item, 'values')
        date_str = self.selected_date.isoformat()
        
        # 인덱스 찾기
        idx = -1
        for i, t in enumerate(self.data['todos'].get(date_str, [])):
            if t['text'] == values[1]:
                idx = i
                break
        
        if idx != -1:
            self.data['todos'][date_str][idx]['done'] = not self.data['todos'][date_str][idx]['done']
            self.save_data()
            self.refresh_info_panel()

    def delete_todo(self):
        selection = self.todo_tree.selection()
        if not selection:
            return
        item = selection[0]
        values = self.todo_tree.item(item, 'values')
        date_str = self.selected_date.isoformat()
        
        # 삭제
        todos = self.data['todos'].get(date_str, [])
        self.data['todos'][date_str] = [t for t in todos if t['text'] != values[1]]
        self.save_data()
        self.refresh_info_panel()

    def set_alarm(self):
        time_str = simpledialog.askstring("알람 설정", "알람 시간을 입력하세요 (HH:MM 형식, 예: 08:00)")
        if not time_str:
            return
        msg = simpledialog.askstring("알람 메시지", "알람 메시지를 입력하세요")
        
        try:
            h, m = map(int, time_str.split(':'))
            alarm_time = dt.now().replace(hour=h, minute=m, second=0).isoformat()
            self.data['alarms'].append({'time': alarm_time, 'message': msg, 'active': True})
            self.save_data()
            messagebox.showinfo("알람 설정", f"{time_str} 에 알람이 설정되었습니다.")
        except:
            messagebox.showerror("오류", "시간 형식이 잘못되었습니다. HH:MM 으로 입력하세요.")

    def check_alarms(self):
        while True:
            now = dt.now()
            current_time_str = now.strftime("%H:%M")
            current_iso = now.isoformat()[:16] # YYYY-MM-DDTHH:MM
            
            alarms_to_remove = []
            for i, alarm in enumerate(self.data['alarms']):
                if alarm['active'] and alarm['time'][:16] == current_iso:
                    # 알람 발생
                    self.root.after(0, lambda m=alarm['message']: self.trigger_alarm(m))
                    alarm['active'] = False
                    alarms_to_remove.append(i)
            
            if alarms_to_remove:
                # 이미 울린 알람은 비활성화 (단순 구현을 위해 리스트 조작 대신 플래그만)
                self.save_data()
            
            import time
            time.sleep(30) # 30 초마다 체크

    def trigger_alarm(self, message):
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        messagebox.showwarning("⏰ 면학 알람", f"{message}\n\n준비하세요!")

    def sync_desktop_memo(self):
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        file_path = os.path.join(desktop, DESKTOP_MEMO_FILE)
        
        date_str = self.selected_date.isoformat()
        schedule = self.data['schedules'].get(date_str, {})
        todos = self.data['todos'].get(date_str, [])
        
        content = f"=== 면학 계획 ({date_str}) ===\n\n"
        type_map = {'8': '8면 (취침)', '1': '1면 (아침)', '2': '2면 (점심)', 'none': '정상 참석'}
        s_type = type_map.get(schedule.get('type', 'none'), '알 수 없음')
        reason = schedule.get('reason', '없음')
        
        content += f"구분: {s_type}\n"
        content += f"사유: {reason}\n\n"
        content += "--- 할 일 목록 ---\n"
        for i, t in enumerate(todos, 1):
            status = "[V]" if t['done'] else "[ ]"
            content += f"{i}. {status} {t['text']}\n"
        
        if not todos:
            content += "등록된 할 일이 없습니다.\n"
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("동기화 완료", f"바탕화면에 '{DESKTOP_MEMO_FILE}' 이 (가) 생성/업데이트 되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"파일 작성 중 오류 발생: {str(e)}")

    def backup_data(self):
        import shutil
        backup_name = f"myeonhak_backup_{dt.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            shutil.copy(DATA_FILE, backup_name)
            messagebox.showinfo("백업 완료", f"현재 폴더에 '{backup_name}' 이 (가) 생성되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"백업 실패: {str(e)}")

    def update_clock(self):
        now = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.root.after(1000, self.update_clock)

if __name__ == "__main__":
    root = tk.Tk()
    app = MyeonhakManager(root)
    root.mainloop()
