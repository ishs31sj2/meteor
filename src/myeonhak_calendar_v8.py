import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import datetime
import holidays
import sys

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("면학 불참 계획 관리자 v8.1 (Stable)")
        self.root.geometry("1000x700")
        
        # 데이터 초기화 및 로드
        self.data_file = "myeonhak_data.json"
        self.current_date = datetime.datetime.now()
        self.selected_date = None
        self.kr_holidays = holidays.SouthKorea()
        
        self.load_data()
        self.create_ui()
        self.update_calendar()

    def load_data(self):
        """데이터 로드 및 구버전 마이그레이션"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                # 구버전 데이터 마이그레이션 (v7 이전 -> v8)
                migrated_data = {}
                for date_str, info in loaded_data.items():
                    if isinstance(info, dict):
                        # 이미 새 형식이면 그대로 사용
                        if 'todos' in info and '8면' in info:
                            migrated_data[date_str] = info
                        else:
                            # 구형식 변환 로직
                            migrated_data[date_str] = {
                                'todos': info.get('todos', []),
                                '8면': {'status': '참가', 'reason': ''},
                                '1면': {'status': '참가', 'reason': ''},
                                '2면': {'status': '참가', 'reason': ''}
                            }
                    else:
                        # 데이터 형식이 완전히 다른 경우 초기화
                        migrated_data[date_str] = {
                            'todos': [],
                            '8면': {'status': '참가', 'reason': ''},
                            '1면': {'status': '참가', 'reason': ''},
                            '2면': {'status': '참가', 'reason': ''}
                        }
                
                self.data = migrated_data
                self.save_data()
            except Exception as e:
                print(f"데이터 로드 오류: {e}")
                self.data = {}
        else:
            self.data = {}

    def save_data(self):
        """데이터 저장"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("저장 오류", f"데이터 저장 중 오류가 발생했습니다:\n{e}")

    def create_ui(self):
        """UI 생성 (레이아웃 오류 수정됨)"""
        # 상단 프레임: 시계 및 네비게이션
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.clock_label = ttk.Label(top_frame, text="", font=("Malgun Gothic", 16, 'bold'))
        self.clock_label.pack(side=tk.LEFT)
        self.update_clock()
        
        nav_frame = ttk.Frame(top_frame)
        nav_frame.pack(side=tk.RIGHT)
        
        ttk.Button(nav_frame, text="< 이전", command=self.prev_month).pack(side=tk.LEFT, padx=2)
        ttk.Label(nav_frame, text="").pack(side=tk.LEFT, padx=5)
        self.month_label = ttk.Label(nav_frame, text="", font=("Malgun Gothic", 14, 'bold'))
        self.month_label.pack(side=tk.LEFT, padx=5)
        ttk.Label(nav_frame, text="").pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="다음 >", command=self.next_month).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="오늘", command=self.go_to_today).pack(side=tk.LEFT, padx=10)

        # 메인 콘텐츠 프레임
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 왼쪽: 달력 영역
        calendar_frame = ttk.LabelFrame(content_frame, text="달력")
        calendar_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 요일 헤더
        days = ['월', '화', '수', '목', '금', '토', '일']
        for i, day in enumerate(days):
            color = 'red' if i >= 5 else 'black'
            lbl = tk.Label(calendar_frame, text=day, font=("Malgun Gothic", 10, 'bold'), fg=color, width=4)
            lbl.grid(row=0, column=i, padx=1, pady=1, sticky='ew')
        
        # 달력 그리드 생성
        self.cal_grid = ttk.Frame(calendar_frame)
        self.cal_grid.grid(row=1, column=0, sticky='nsew')
        for i in range(7):
            calendar_frame.grid_columnconfigure(i, weight=1)
        calendar_frame.grid_rowconfigure(1, weight=1)
        
        # 오른쪽: 상세 정보 영역
        detail_frame = ttk.LabelFrame(content_frame, text="상세 정보 및 관리")
        detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        # 날짜 표시
        self.date_info_label = ttk.Label(detail_frame, text="날짜를 선택해주세요", font=("Malgun Gothic", 12, 'bold'))
        self.date_info_label.pack(pady=10)
        
        # 면학 상태 설정 영역
        status_frame = ttk.LabelFrame(detail_frame, text="면학 상태 설정")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.myeonhak_vars = {}
        self.myeonhak_reasons = {}
        
        for myeong in ['8면', '1면', '2면']:
            frame = ttk.Frame(status_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame, text=f"{myeong}: ", width=5).pack(side=tk.LEFT)
            
            var = tk.StringVar(value='참가')
            cb = ttk.Combobox(frame, textvariable=var, values=['참가', '불참'], width=8, state='readonly')
            cb.pack(side=tk.LEFT, padx=5)
            cb.bind('<<ComboboxSelected>>', lambda e, m=myeong: self.on_status_change(m))
            
            reason_entry = ttk.Entry(frame, width=20)
            reason_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            reason_entry.bind('<KeyRelease>', lambda e, m=myeong: self.on_reason_change(m))
            
            self.myeonhak_vars[myeong] = var
            self.myeonhak_reasons[myeong] = reason_entry

        # ToDo 영역
        todo_frame = ttk.LabelFrame(detail_frame, text="할 일 (ToDo)")
        todo_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.todo_listbox = tk.Listbox(todo_frame, font=("Malgun Gothic", 10), height=8)
        self.todo_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.todo_listbox.bind('<Double-Button-1>', self.toggle_todo_done)
        
        todo_btn_frame = ttk.Frame(todo_frame)
        todo_btn_frame.pack(fill=tk.X)
        
        ttk.Button(todo_btn_frame, text="추가", command=self.add_todo).pack(side=tk.LEFT, padx=2)
        ttk.Button(todo_btn_frame, text="삭제", command=self.delete_todo).pack(side=tk.LEFT, padx=2)
        ttk.Button(todo_btn_frame, text="완료토글", command=self.toggle_todo_done).pack(side=tk.LEFT, padx=2)

    def update_clock(self):
        now = datetime.datetime.now()
        self.clock_label.config(text=now.strftime("%Y-%m-%d %H:%M:%S"))
        self.root.after(1000, self.update_clock)

    def update_calendar(self):
        # 그리드 초기화
        for widget in self.cal_grid.winfo_children():
            widget.destroy()
            
        year = self.current_date.year
        month = self.current_date.month
        self.month_label.config(text=f"{year}년 {month}월")
        
        # 첫날 요일과 마지막 날 계산
        first_day = datetime.date(year, month, 1)
        if month == 12:
            next_month = datetime.date(year+1, 1, 1)
        else:
            next_month = datetime.date(year, month+1, 1)
        
        start_weekday = first_day.weekday() # 0=Mon, 6=Sun
        days_in_month = (next_month - first_day).days
        
        # 날짜 배치
        day_count = 1
        for row in range(6):
            for col in range(7):
                if row == 0 and col < start_weekday:
                    continue
                if day_count > days_in_month:
                    break
                
                current_day = datetime.date(year, month, day_count)
                day_str = current_day.strftime("%Y-%m-%d")
                
                # 공휴일 확인
                is_holiday = day_str in self.kr_holidays
                holiday_name = self.kr_holidays.get(day_str, "")
                
                # 버튼 텍스트 생성
                btn_text = f"{day_count}"
                if is_holiday:
                    btn_text += f"\n{holiday_name}"
                
                # 색상 결정
                bg_color = '#ffcccc' if is_holiday else '#ffffff'
                fg_color = 'red' if is_holiday else 'black'
                
                # 토/일 색상
                if col == 5: # 토요일
                    fg_color = 'blue'
                elif col == 6: # 일요일
                    fg_color = 'red'
                
                btn = tk.Button(self.cal_grid, text=btn_text, width=4, height=2, 
                                bg=bg_color, fg=fg_color,
                                command=lambda d=day_count: self.select_date(d))
                btn.grid(row=row+1, column=col, padx=1, pady=1, sticky='nsew')
                
                # 선택된 날짜 강조
                if self.selected_date and self.selected_date.day == day_count and \
                   self.selected_date.month == month and self.selected_date.year == year:
                    btn.config(relief=tk.SUNKEN, bd=3)
                
                day_count += 1

    def select_date(self, day):
        self.selected_date = datetime.date(self.current_date.year, self.current_date.month, day)
        date_str = self.selected_date.strftime("%Y-%m-%d")
        
        self.date_info_label.config(text=f"{date_str} 상세 정보")
        
        # 데이터 초기화 (없으면 생성)
        if date_str not in self.data:
            self.data[date_str] = {
                'todos': [],
                '8면': {'status': '참가', 'reason': ''},
                '1면': {'status': '참가', 'reason': ''},
                '2면': {'status': '참가', 'reason': ''}
            }
        
        current_info = self.data[date_str]
        
        # 면학 상태 업데이트
        for myeong in ['8면', '1면', '2면']:
            info = current_info.get(myeong, {'status': '참가', 'reason': ''})
            self.myeonhak_vars[myeong].set(info['status'])
            self.myeonhak_reasons[myeong].delete(0, tk.END)
            self.myeonhak_reasons[myeong].insert(0, info['reason'])
        
        # ToDo 업데이트
        self.todo_listbox.delete(0, tk.END)
        for todo in current_info.get('todos', []):
            prefix = "[✓] " if todo.get('done', False) else "[ ] "
            self.todo_listbox.insert(tk.END, prefix + todo['text'])
        
        self.update_calendar() # 선택 강조를 위해 다시 그리기

    def on_status_change(self, myeong):
        if not self.selected_date: return
        date_str = self.selected_date.strftime("%Y-%m-%d")
        self.data[date_str][myeong]['status'] = self.myeonhak_vars[myeong].get()
        self.save_data()

    def on_reason_change(self, myeong):
        if not self.selected_date: return
        date_str = self.selected_date.strftime("%Y-%m-%d")
        self.data[date_str][myeong]['reason'] = self.myeonhak_reasons[myeong].get()
        self.save_data()

    def add_todo(self):
        if not self.selected_date: 
            messagebox.showwarning("알림", "날짜를 먼저 선택해주세요.")
            return
        text = simpledialog.askstring("할 일 추가", "할 일을 입력하세요:")
        if text:
            date_str = self.selected_date.strftime("%Y-%m-%d")
            self.data[date_str]['todos'].append({'text': text, 'done': False})
            self.save_data()
            self.select_date(self.selected_date.day)

    def delete_todo(self):
        if not self.selected_date: return
        sel = self.todo_listbox.curselection()
        if sel:
            idx = sel[0]
            date_str = self.selected_date.strftime("%Y-%m-%d")
            del self.data[date_str]['todos'][idx]
            self.save_data()
            self.select_date(self.selected_date.day)

    def toggle_todo_done(self, event=None):
        if not self.selected_date: return
        sel = self.todo_listbox.curselection()
        if sel:
            idx = sel[0]
            date_str = self.selected_date.strftime("%Y-%m-%d")
            todo = self.data[date_str]['todos'][idx]
            todo['done'] = not todo['done']
            self.save_data()
            self.select_date(self.selected_date.day)

    def prev_month(self):
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year-1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month-1)
        self.update_calendar()

    def next_month(self):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year+1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month+1)
        self.update_calendar()

    def go_to_today(self):
        self.current_date = datetime.datetime.now()
        self.selected_date = None
        self.date_info_label.config(text="날짜를 선택해주세요")
        self.update_calendar()

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()
