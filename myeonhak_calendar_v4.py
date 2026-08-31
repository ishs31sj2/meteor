# -*- coding: utf-8 -*-
"""
Myeonhak Calendar Ultimate - 면학 불참 계획 관리자
기능: 달력 UI, 면학 관리, 할 일, 알람, 바탕화면 메모 동기화, 공휴일 연동
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import datetime
import calendar
import threading
import time
import winsound  # Windows 전용 사운드 모듈

# 외부 라이브러리 시도 (없으면 수동 설치 안내)
try:
    import holidays
except ImportError:
    print("holidays 라이브러리가 없습니다. pip install holidays 필요")
    holidays = None

class MyeonhakApp:
    def __init__(self, root):
        self.root = root
        self.root.title("면학 불참 계획 관리자 Ultimate")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 데이터 파일 경로
        self.data_file = "myeonhak_data.json"
        self.desktop_note_path = os.path.join(os.path.expanduser("~"), "Desktop", "면학_메모.txt")
        
        # 현재 날짜 상태
        self.current_date = datetime.date.today()
        self.selected_date = self.current_date
        
        # 데이터 로드
        self.data = self.load_data()
        
        # 알람 리스트
        self.alarms = self.data.get("alarms", [])
        self.alarm_thread_running = False
        
        # 스타일 설정
        self.setup_styles()
        
        # UI 구성
        self.create_ui()
        
        # 달력 그리기
        self.draw_calendar()
        
        # 알람 감시 스레드 시작
        self.start_alarm_monitor()
        
        # 바탕화면 메모 초기 동기화
        self.sync_desktop_note()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # 색상 팔레트 (다크 테마)
        self.colors = {
            'bg': '#2b2b2b',
            'panel': '#3c3f41',
            'text': '#ffffff',
            'accent': '#4a90e2',
            'highlight': '#50fa7b',
            'danger': '#ff5555',
            'warning': '#ffb86c',
            'calendar_bg': '#282a36',
            'weekend': '#ff79c6',
            'holiday': '#ff5555',
            'today': '#44475a'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # 폰트
        self.font_title = ("맑은 고딕", 16, "bold")
        self.font_normal = ("맑은 고딕", 10)
        self.font_small = ("맑은 고딕", 9)

    def create_ui(self):
        # 상단 헤더 (시계 + 제목)
        header_frame = tk.Frame(self.root, bg=self.colors['panel'], height=60)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="📅 면학 불참 계획 관리자", 
                               font=self.font_title, bg=self.colors['panel'], fg=self.colors['text'])
        title_label.pack(side=tk.LEFT, padx=20)
        
        self.clock_label = tk.Label(header_frame, text="", font=("Consolas", 14, "bold"), 
                                    bg=self.colors['panel'], fg=self.colors['highlight'])
        self.clock_label.pack(side=tk.RIGHT, padx=20)
        self.update_clock()
        
        # 메인 컨테이너 (좌: 달력, 우: 상세정보)
        main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 왼쪽 패널 (달력)
        left_frame = tk.Frame(main_container, bg=self.colors['calendar_bg'])
        main_container.add(left_frame, width=500)
        
        # 달력 네비게이션
        nav_frame = tk.Frame(left_frame, bg=self.colors['calendar_bg'])
        nav_frame.pack(fill=tk.X, pady=10)
        
        btn_prev = tk.Button(nav_frame, text="<", command=self.prev_month, 
                             bg=self.colors['panel'], fg=self.colors['text'], width=5)
        btn_prev.pack(side=tk.LEFT, padx=10)
        
        self.lbl_month = tk.Label(nav_frame, text="", font=self.font_title, 
                                  bg=self.colors['calendar_bg'], fg=self.colors['text'])
        self.lbl_month.pack(side=tk.LEFT, expand=True)
        
        btn_next = tk.Button(nav_frame, text=">", command=self.next_month, 
                             bg=self.colors['panel'], fg=self.colors['text'], width=5)
        btn_next.pack(side=tk.RIGHT, padx=10)
        
        btn_today = tk.Button(nav_frame, text="오늘", command=self.go_today, 
                              bg=self.colors['accent'], fg=self.colors['text'], width=5)
        btn_today.pack(side=tk.RIGHT, padx=5)
        
        # 요일 헤더
        days_header = ["월", "화", "수", "목", "금", "토", "일"]
        days_frame = tk.Frame(left_frame, bg=self.colors['calendar_bg'])
        days_frame.pack(fill=tk.X, padx=10)
        for i, day in enumerate(days_header):
            color = self.colors['weekend'] if i >= 5 else self.colors['text']
            lbl = tk.Label(days_frame, text=day, font=self.font_normal, 
                           bg=self.colors['calendar_bg'], fg=color, width=10, height=2)
            lbl.pack(side=tk.LEFT, expand=True)
        
        # 달력 그리드
        self.calendar_grid = tk.Frame(left_frame, bg=self.colors['calendar_bg'])
        self.calendar_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 오른쪽 패널 (상세 정보)
        right_frame = tk.Frame(main_container, bg=self.colors['panel'])
        main_container.add(right_frame)
        
        # 날짜 선택 표시
        date_info_frame = tk.Frame(right_frame, bg=self.colors['panel'])
        date_info_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(date_info_frame, text="선택된 날짜:", font=self.font_normal, 
                 bg=self.colors['panel'], fg=self.colors['text']).pack(side=tk.LEFT)
        self.lbl_selected_date = tk.Label(date_info_frame, text="", font=("맑은 고딕", 12, "bold"), 
                                          bg=self.colors['panel'], fg=self.colors['accent'])
        self.lbl_selected_date.pack(side=tk.LEFT, padx=10)
        
        # 면학 설정 영역
        myeonhak_frame = tk.LabelFrame(right_frame, text="📚 면학 설정 (평일만)", 
                                       font=self.font_normal, bg=self.colors['panel'], fg=self.colors['text'])
        myeonhak_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.myeonhak_vars = {}
        types = [("8 면", "type8"), ("1 면", "type1"), ("2 면", "type2")]
        
        for name, key in types:
            frame = tk.Frame(myeonhak_frame, bg=self.colors['panel'])
            frame.pack(fill=tk.X, pady=5)
            
            var = tk.BooleanVar(value=False)
            self.myeonhak_vars[key] = var
            
            chk = tk.Checkbutton(frame, text=f"{name} 불참 신청", variable=var, 
                                 font=self.font_normal, bg=self.colors['panel'], 
                                 fg=self.colors['text'], selectcolor=self.colors['bg'],
                                 activebackground=self.colors['panel'], activeforeground=self.colors['text'])
            chk.pack(side=tk.LEFT)
            
            btn_save = tk.Button(frame, text="저장", command=lambda k=key: self.save_myeonhak(k),
                                 bg=self.colors['accent'], fg=self.colors['text'], width=5)
            btn_save.pack(side=tk.RIGHT, padx=5)
        
        # 할 일 목록
        todo_frame = tk.LabelFrame(right_frame, text="✅ 할 일 목록", 
                                   font=self.font_normal, bg=self.colors['panel'], fg=self.colors['text'])
        todo_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 할 일 입력
        input_frame = tk.Frame(todo_frame, bg=self.colors['panel'])
        input_frame.pack(fill=tk.X, pady=5)
        
        self.todo_entry = tk.Entry(input_frame, font=self.font_normal, bg=self.colors['bg'], fg=self.colors['text'])
        self.todo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.todo_entry.bind("<Return>", lambda e: self.add_todo())
        
        btn_add = tk.Button(input_frame, text="추가", command=self.add_todo,
                            bg=self.colors['highlight'], fg=self.colors['bg'], width=5)
        btn_add.pack(side=tk.RIGHT, padx=5)
        
        # 할 일 리스트박스
        self.todo_listbox = tk.Listbox(todo_frame, font=self.font_normal, 
                                       bg=self.colors['bg'], fg=self.colors['text'],
                                       selectbackground=self.colors['accent'], selectforeground=self.colors['text'],
                                       height=10)
        self.todo_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.todo_listbox.bind("<Double-Button-1>", self.toggle_todo_complete)
        
        btn_del = tk.Button(todo_frame, text="삭제", command=self.delete_todo,
                            bg=self.colors['danger'], fg=self.colors['text'], width=10)
        btn_del.pack(pady=5)
        
        # 하단 버튼 (알람, 메모)
        bottom_frame = tk.Frame(right_frame, bg=self.colors['panel'])
        bottom_frame.pack(fill=tk.X, padx=20, pady=10)
        
        btn_alarm = tk.Button(bottom_frame, text="⏰ 알람 설정", command=self.set_alarm,
                              bg=self.colors['warning'], fg=self.colors['bg'], width=15)
        btn_alarm.pack(side=tk.LEFT, padx=5)
        
        btn_note = tk.Button(bottom_frame, text="📝 바탕화면 메모 동기화", command=self.sync_desktop_note,
                             bg=self.colors['accent'], fg=self.colors['text'], width=20)
        btn_note.pack(side=tk.LEFT, padx=5)
        
        # 알람 상태 라벨
        self.lbl_alarm_status = tk.Label(bottom_frame, text="", font=self.font_small, 
                                         bg=self.colors['panel'], fg=self.colors['warning'])
        self.lbl_alarm_status.pack(side=tk.LEFT, padx=10)

    def update_clock(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.root.after(1000, self.update_clock)

    def draw_calendar(self):
        # 기존 위젯 제거
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()
            
        year = self.current_date.year
        month = self.current_date.month
        
        self.lbl_month.config(text=f"{year}년 {month}월")
        
        # 공휴일 목록 가져오기 (한국)
        kr_holidays = {}
        if holidays:
            kr_holidays = holidays.Korea(years=year)
        
        # 캘린더 계산
        cal = calendar.Calendar(firstweekday=calendar.MONDAY)
        month_days = cal.monthdayscalendar(year, month)
        
        # 오늘 날짜
        today = datetime.date.today()
        
        # 요일별 색상 결정 함수
        def get_day_color(day, weekday):
            if datetime.date(year, month, day) in kr_holidays:
                return self.colors['holiday']
            if weekday >= 5: # 주말
                return self.colors['weekend']
            return self.colors['text']
        
        # 그리드 채우기
        for week_idx, week in enumerate(month_days):
            for day_idx, day in enumerate(week):
                if day == 0:
                    continue
                
                current_day_date = datetime.date(year, month, day)
                is_today = (current_day_date == today)
                is_selected = (current_day_date == self.selected_date)
                
                # 배경색 결정
                bg_color = self.colors['calendar_bg']
                if is_today:
                    bg_color = self.colors['today']
                if is_selected:
                    bg_color = self.colors['accent']
                
                # 텍스트 색상
                fg_color = get_day_color(day, day_idx)
                
                # 면학 일정 있는지 확인 (간단히 점 표시용)
                date_str = current_day_date.strftime("%Y-%m-%d")
                has_plan = ""
                if date_str in self.data.get("plans", {}):
                    plan = self.data["plans"][date_str]
                    indicators = []
                    if plan.get("type8"): indicators.append("8")
                    if plan.get("type1"): indicators.append("1")
                    if plan.get("type2"): indicators.append("2")
                    if indicators:
                        has_plan = f" [{','.join(indicators)}]"
                
                # 공휴일 이름 추가
                holiday_name = ""
                if current_day_date in kr_holidays:
                    holiday_name = f"\n{kr_holidays[current_day_date]}"
                
                btn_text = f"{day}{has_plan}{holiday_name}"
                
                btn = tk.Button(self.calendar_grid, text=btn_text, font=self.font_normal,
                                bg=bg_color, fg=fg_color, width=10, height=4,
                                command=lambda d=day: self.select_date(d))
                btn.grid(row=week_idx, column=day_idx, padx=2, pady=2, sticky="nsew")
                
                # 그리드 가중치 설정
                self.calendar_grid.grid_columnconfigure(day_idx, weight=1)
                self.calendar_grid.grid_rowconfigure(week_idx, weight=1)

    def prev_month(self):
        prev = self.current_date.replace(day=1) - datetime.timedelta(days=1)
        self.current_date = prev.replace(day=1)
        self.draw_calendar()
        
    def next_month(self):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year+1, month=1, day=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month+1, day=1)
        self.draw_calendar()
        
    def go_today(self):
        self.current_date = datetime.date.today()
        self.selected_date = self.current_date
        self.draw_calendar()
        self.update_detail_panel()
        
    def select_date(self, day):
        try:
            self.selected_date = datetime.date(self.current_date.year, self.current_date.month, day)
            self.draw_calendar() # 선택 강조를 위해 다시 그림
            self.update_detail_panel()
        except ValueError:
            pass

    def update_detail_panel(self):
        date_str = self.selected_date.strftime("%Y-%m-%d")
        self.lbl_selected_date.config(text=date_str)
        
        # 요일 확인 (평일만 면학 설정 활성화)
        weekday = self.selected_date.weekday()
        is_weekday = weekday < 5
        
        # 면학 체크박스 상태 복원
        plan = self.data.get("plans", {}).get(date_str, {})
        
        for key, var in self.myeonhak_vars.items():
            var.set(plan.get(key, False))
            # 평일이 아니면 비활성화
            # widget 상태를 직접 제어하려면 해당 위젯을 찾아야 함 (간단화를 위해 생략하거나 구현 가능)
            
        # 할 일 목록 복원
        self.todo_listbox.delete(0, tk.END)
        todos = self.data.get("todos", {}).get(date_str, [])
        for todo in todos:
            display = f"[완료] {todo}" if todo.startswith("[완료]") else todo
            self.todo_listbox.insert(tk.END, display)
            
        # 알람 상태 업데이트
        self.update_alarm_status_label()

    def save_myeonhak(self, type_key):
        date_str = self.selected_date.strftime("%Y-%m-%d")
        weekday = self.selected_date.weekday()
        
        if weekday >= 5:
            messagebox.showwarning("경고", "면학 설정은 평일 (월~금) 에만 가능합니다.")
            return
            
        if "plans" not in self.data:
            self.data["plans"] = {}
        if date_str not in self.data["plans"]:
            self.data["plans"][date_str] = {}
            
        self.data["plans"][date_str][type_key] = self.myeonhak_vars[type_key].get()
        self.save_data()
        self.draw_calendar() # 업데이트 반영
        messagebox.showinfo("저장 완료", f"{date_str} {type_key} 상태가 저장되었습니다.")

    def add_todo(self):
        task = self.todo_entry.get().strip()
        if not task:
            return
            
        date_str = self.selected_date.strftime("%Y-%m-%d")
        if "todos" not in self.data:
            self.data["todos"] = {}
        if date_str not in self.data["todos"]:
            self.data["todos"][date_str] = []
            
        self.data["todos"][date_str].append(task)
        self.todo_entry.delete(0, tk.END)
        self.save_data()
        self.update_detail_panel()

    def toggle_todo_complete(self, event):
        selection = self.todo_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        task = self.todo_listbox.get(index)
        
        date_str = self.selected_date.strftime("%Y-%m-%d")
        todos = self.data.get("todos", {}).get(date_str, [])
        
        if index < len(todos):
            current = todos[index]
            if current.startswith("[완료]"):
                todos[index] = current.replace("[완료] ", "")
            else:
                todos[index] = "[완료] " + current
            self.save_data()
            self.update_detail_panel()

    def delete_todo(self):
        selection = self.todo_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        
        date_str = self.selected_date.strftime("%Y-%m-%d")
        todos = self.data.get("todos", {}).get(date_str, [])
        
        if index < len(todos):
            del todos[index]
            self.save_data()
            self.update_detail_panel()

    def set_alarm(self):
        # 간단한 알람 설정 다이얼로그
        top = tk.Toplevel(self.root)
        top.title("알람 설정")
        top.geometry("300x150")
        top.configure(bg=self.colors['panel'])
        
        tk.Label(top, text="시간 (HH:MM)", font=self.font_normal, bg=self.colors['panel'], fg=self.colors['text']).pack(pady=5)
        time_entry = tk.Entry(top, font=self.font_normal)
        time_entry.pack(pady=5)
        time_entry.insert(0, "08:00")
        
        tk.Label(top, text="메시지", font=self.font_normal, bg=self.colors['panel'], fg=self.colors['text']).pack(pady=5)
        msg_entry = tk.Entry(top, font=self.font_normal)
        msg_entry.pack(pady=5)
        msg_entry.insert(0, "면학 시간입니다!")
        
        def save_alarm():
            t = time_entry.get()
            m = msg_entry.get()
            if t and m:
                self.alarms.append({"time": t, "message": m, "active": True})
                self.data["alarms"] = self.alarms
                self.save_data()
                self.update_alarm_status_label()
                messagebox.showinfo("알람 설정", f"{t} 에 알람이 설정되었습니다.")
                top.destroy()
                
        tk.Button(top, text="설정", command=save_alarm, bg=self.colors['accent'], fg=self.colors['text']).pack(pady=10)

    def update_alarm_status_label(self):
        active_count = sum(1 for a in self.alarms if a.get("active", False))
        self.lbl_alarm_status.config(text=f"활성 알람: {active_count}개")

    def start_alarm_monitor(self):
        if self.alarm_thread_running:
            return
        self.alarm_thread_running = True
        
        def monitor():
            while self.alarm_thread_running:
                now = datetime.datetime.now().strftime("%H:%M")
                current_sec = datetime.datetime.now().second
                
                # 매 분 0 초에 확인
                if current_sec == 0:
                    for alarm in self.alarms:
                        if alarm.get("active", False) and alarm["time"] == now:
                            # 알람 발생
                            self.root.after(0, lambda msg=alarm["message"]: self.trigger_alarm(msg))
                            
                time.sleep(1)
                
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    def trigger_alarm(self, message):
        winsound.Beep(1000, 500) # 1kHz, 0.5 초
        winsound.Beep(1000, 500)
        messagebox.showwarning("⏰ 알람", message)

    def sync_desktop_note(self):
        """바탕화면의 면학_메모.txt 와 동기화"""
        date_str = self.selected_date.strftime("%Y-%m-%d")
        todos = self.data.get("todos", {}).get(date_str, [])
        plan = self.data.get("plans", {}).get(date_str, {})
        
        content = f"=== 면학 계획 메모 ({date_str}) ===\n\n"
        content += "[면학 설정]\n"
        plan_text = []
        if plan.get("type8"): plan_text.append("8 면 불참")
        if plan.get("type1"): plan_text.append("1 면 불참")
        if plan.get("type2"): plan_text.append("2 면 불참")
        content += ", ".join(plan_text) if plan_text else "없음"
        content += "\n\n[할 일 목록]\n"
        for todo in todos:
            content += f"- {todo}\n"
            
        try:
            with open(self.desktop_note_path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("동기화 완료", f"바탕화면에 '면학_메모.txt' 가 업데이트되었습니다.\n경로: {self.desktop_note_path}")
        except Exception as e:
            messagebox.showerror("오류", f"파일 작성 중 오류 발생: {str(e)}")

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {"plans": {}, "todos": {}, "alarms": []}

    def save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = MyeonhakApp(root)
    root.mainloop()
