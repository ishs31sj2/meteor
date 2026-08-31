# -*- coding: utf-8 -*-
"""
면학 불참 계획 관리자 (Ultimate v5)
- 8 면, 1 면, 2 면 면불 사유 입력 지원
- 날짜별 상세 ToDo 관리
- 실시간 시계 및 한국 공휴일 자동 연동
- 알람 기능 및 바탕화면 메모 동기화
- Windows 호환성 강화 (인코딩 utf-8 고정)
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import datetime
import calendar
import threading
import time
import winsound
from pathlib import Path

# --- 데이터 관리 클래스 ---
class DataManager:
    def __init__(self):
        self.data_file = "myeonhak_data.json"
        self.data = self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"데이터 로드 오류: {e}")
                return {"schedules": {}, "todos": {}, "alarms": []}
        return {"schedules": {}, "todos": {}, "alarms": []}
    
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
    
    def get_schedule(self, date_str):
        return self.data["schedules"].get(date_str, {"type": None, "reason": "", "memo": ""})
    
    def set_schedule(self, date_str, m_type, reason, memo=""):
        self.data["schedules"][date_str] = {
            "type": m_type,
            "reason": reason,
            "memo": memo
        }
        self.save_data()
    
    def get_todos(self, date_str):
        return self.data["todos"].get(date_str, [])
    
    def add_todo(self, date_str, todo_text):
        if date_str not in self.data["todos"]:
            self.data["todos"][date_str] = []
        self.data["todos"][date_str].append({"text": todo_text, "done": False})
        self.save_data()
    
    def toggle_todo(self, date_str, index):
        if date_str in self.data["todos"] and 0 <= index < len(self.data["todos"][date_str]):
            self.data["todos"][date_str][index]["done"] = not self.data["todos"][date_str][index]["done"]
            self.save_data()
    
    def delete_todo(self, date_str, index):
        if date_str in self.data["todos"] and 0 <= index < len(self.data["todos"][date_str]):
            del self.data["todos"][date_str][index]
            self.save_data()
    
    def get_alarms(self):
        return self.data.get("alarms", [])
    
    def add_alarm(self, time_str, message):
        self.data["alarms"].append({"time": time_str, "message": message, "active": True})
        self.save_data()
    
    def remove_alarm(self, index):
        if 0 <= index < len(self.data["alarms"]):
            del self.data["alarms"][index]
            self.save_data()

# --- 공휴일 관리 ---
def get_korean_holidays(year):
    try:
        import holidays
        kr_holidays = holidays.Korea(years=year)
        return {date: name for date, name in kr_holidays.items()}
    except ImportError:
        return {}
    except Exception:
        return {}

# --- 메인 애플리케이션 ---
class MyeonhakApp:
    def __init__(self, root):
        self.root = root
        self.root.title("면학 불참 계획 관리자 (Ultimate v5)")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # 데이터 매니저 초기화
        self.dm = DataManager()
        
        # 현재 날짜 설정
        self.current_date = datetime.date.today()
        self.selected_date = self.current_date
        
        # 스타일 설정
        self.colors = {
            "bg": "#f0f2f5",
            "panel": "#ffffff",
            "primary": "#4a90e2",
            "text": "#333333",
            "8men": "#e74c3c",  # 빨강
            "1men": "#1abc9c",  # 민트
            "2men": "#f1c40f",  # 노랑
            "holiday": "#e74c3c"
        }
        
        self.setup_ui()
        self.update_calendar()
        self.load_selected_date_info()
        self.start_alarm_checker()
    
    def setup_ui(self):
        # 상단 프레임 (시계 + 타이틀)
        top_frame = tk.Frame(self.root, bg=self.colors["primary"], height=60)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)
        
        title_label = tk.Label(top_frame, text="📅 면학 불참 계획 관리자", 
                               font=("Malgun Gothic", 18, "bold"), bg=self.colors["primary"], fg="white")
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        self.clock_label = tk.Label(top_frame, text="", 
                                    font=("Consolas", 16, "bold"), bg=self.colors["primary"], fg="white")
        self.clock_label.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # 메인 컨테이너
        main_container = tk.Frame(self.root, bg=self.colors["bg"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 왼쪽: 달력 패널
        left_panel = tk.Frame(main_container, bg=self.colors["panel"], relief=tk.RAISED, bd=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 달력 네비게이션
        nav_frame = tk.Frame(left_panel, bg=self.colors["panel"])
        nav_frame.pack(fill=tk.X, pady=10)
        
        btn_prev = tk.Button(nav_frame, text="< 이전", command=self.prev_month, bg="#ddd", font=("Malgun Gothic", 10))
        btn_prev.pack(side=tk.LEFT, padx=10)
        
        self.lbl_month = tk.Label(nav_frame, text="", font=("Malgun Gothic", 14, "bold"), bg=self.colors["panel"])
        self.lbl_month.pack(side=tk.LEFT, expand=True)
        
        btn_next = tk.Button(nav_frame, text="다음 >", command=self.next_month, bg="#ddd", font=("Malgun Gothic", 10))
        btn_next.pack(side=tk.RIGHT, padx=10)
        
        btn_today = tk.Button(nav_frame, text="오늘", command=self.go_today, bg=self.colors["primary"], fg="white", font=("Malgun Gothic", 10))
        btn_today.pack(side=tk.RIGHT, padx=5)
        
        # 달력 그리드
        self.calendar_frame = tk.Frame(left_panel, bg=self.colors["panel"])
        self.calendar_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 요일 헤더
        days = ["월", "화", "수", "목", "금", "토", "일"]
        for i, day in enumerate(days):
            color = "red" if i >= 5 else "black"
            lbl = tk.Label(self.calendar_frame, text=day, font=("Malgun Gothic", 10, "bold"), 
                           fg=color, bg=self.colors["panel"], relief=tk.SOLID, bd=1)
            lbl.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
        
        for i in range(6):
            self.calendar_frame.grid_rowconfigure(i+1, weight=1)
        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1)
        
        self.day_buttons = []
        for r in range(1, 7):
            row_btns = []
            for c in range(7):
                btn = tk.Button(self.calendar_frame, text="", font=("Malgun Gothic", 10), 
                                bg=self.colors["panel"], relief=tk.FLAT, cursor="hand2",
                                command=lambda d=None: None) # 나중에 재할당
                btn.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                row_btns.append(btn)
            self.day_buttons.append(row_btns)
        
        # 오른쪽: 정보 및 할 일 패널
        right_panel = tk.Frame(main_container, bg=self.colors["panel"], relief=tk.RAISED, bd=1, width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_panel.pack_propagate(False)
        
        # 선택된 날짜 표시
        date_header = tk.Label(right_panel, text="선택 날짜", font=("Malgun Gothic", 16, "bold"), 
                               bg=self.colors["panel"], fg=self.colors["primary"])
        date_header.pack(pady=15)
        
        self.lbl_selected_date = tk.Label(right_panel, text="", font=("Malgun Gothic", 14), bg=self.colors["panel"])
        self.lbl_selected_date.pack()
        
        # 면학 설정 프레임
        mf_frame = tk.LabelFrame(right_panel, text="면학 설정 (8 면/1 면/2 면)", font=("Malgun Gothic", 12, "bold"), 
                                 bg=self.colors["panel"], fg=self.colors["text"])
        mf_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(mf_frame, text="구분:", bg=self.colors["panel"]).grid(row=0, column=0, sticky="w", pady=5)
        self.combo_type = ttk.Combobox(mf_frame, values=["없음", "8 면", "1 면", "2 면"], state="readonly", width=15)
        self.combo_type.grid(row=0, column=1, pady=5, padx=5)
        self.combo_type.bind("<<ComboboxSelected>>", self.on_type_change)
        
        tk.Label(mf_frame, text="사유:", bg=self.colors["panel"]).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_reason = tk.Entry(mf_frame, width=18)
        self.entry_reason.grid(row=1, column=1, pady=5, padx=5)
        self.entry_reason.bind("<KeyRelease>", lambda e: self.save_schedule())
        
        tk.Label(mf_frame, text="메모:", bg=self.colors["panel"]).grid(row=2, column=0, sticky="nw", pady=5)
        self.text_memo = tk.Text(mf_frame, height=4, width=18)
        self.text_memo.grid(row=2, column=1, pady=5, padx=5)
        self.text_memo.bind("<KeyRelease>", lambda e: self.save_schedule())
        
        # 할 일 관리 프레임
        todo_frame = tk.LabelFrame(right_panel, text="할 일 (ToDo)", font=("Malgun Gothic", 12, "bold"), 
                                   bg=self.colors["panel"], fg=self.colors["text"])
        todo_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        input_frame = tk.Frame(todo_frame, bg=self.colors["panel"])
        input_frame.pack(fill=tk.X, pady=5)
        
        self.entry_todo = tk.Entry(input_frame, font=("Malgun Gothic", 10))
        self.entry_todo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry_todo.bind("<Return>", lambda e: self.add_todo_item())
        
        btn_add = tk.Button(input_frame, text="추가", command=self.add_todo_item, bg=self.colors["primary"], fg="white")
        btn_add.pack(side=tk.RIGHT)
        
        self.todo_listbox = tk.Listbox(todo_frame, font=("Malgun Gothic", 10), height=10)
        self.todo_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.todo_listbox.bind("<Double-Button-1>", self.toggle_todo_item)
        
        btn_del = tk.Button(todo_frame, text="삭제", command=self.delete_todo_item, bg="#e74c3c", fg="white")
        btn_del.pack(fill=tk.X, pady=5)
        
        # 하단 버튼 (알람, 바탕화면)
        bottom_frame = tk.Frame(right_panel, bg=self.colors["panel"])
        bottom_frame.pack(fill=tk.X, padx=15, pady=10)
        
        btn_alarm = tk.Button(bottom_frame, text="⏰ 알람 설정", command=self.set_alarm, bg="#f39c12", fg="white", height=2)
        btn_alarm.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_sync = tk.Button(bottom_frame, text="📝 바탕화면 동기화", command=self.sync_desktop, bg="#8e44ad", fg="white", height=2)
        btn_sync.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 알람 목록 표시 (작게)
        self.lbl_alarm_status = tk.Label(right_panel, text="등록된 알람 없음", font=("Malgun Gothic", 9), 
                                         bg=self.colors["panel"], fg="#7f8c8d")
        self.lbl_alarm_status.pack(pady=5)

    def update_calendar(self):
        year = self.current_date.year
        month = self.current_date.month
        
        self.lbl_month.config(text=f"{year}년 {month}월")
        
        # 공휴일 가져오기
        holidays_dict = get_korean_holidays(year)
        
        # 첫날 요일과 마지막 날 계산
        first_day_weekday = calendar.weekday(year, month, 1) # 0=월
        last_day = calendar.monthrange(year, month)[1]
        
        # 버튼 초기화
        for row in self.day_buttons:
            for btn in row:
                btn.config(text="", bg=self.colors["panel"], state=tk.DISABLED, command=None)
        
        # 날짜 채우기
        day_count = 1
        start_row = 0
        start_col = first_day_weekday
        
        current_date_obj = datetime.date.today()
        
        for r in range(6):
            for c in range(7):
                if r == 0 and c < start_col:
                    continue
                if day_count > last_day:
                    break
                
                date_val = day_count
                date_str = f"{year}-{month:02d}-{day_count:02d}"
                current_full_date = datetime.date(year, month, day_count)
                
                btn = self.day_buttons[r][c]
                btn.config(text=str(date_val), state=tk.NORMAL)
                
                # 스타일 적용
                bg_color = self.colors["panel"]
                fg_color = "black"
                
                # 주말 색상
                if c >= 5: # 토, 일
                    fg_color = "red" if c == 6 else "blue"
                
                # 공휴일 체크
                if current_full_date in holidays_dict:
                    bg_color = "#ffebee" # 연한 빨강
                    fg_color = "red"
                
                # 오늘 날짜 강조
                if current_full_date == current_date_obj:
                    bg_color = "#d6eaf8"
                    btn.config(font=("Malgun Gothic", 10, "bold"))
                else:
                    btn.config(font=("Malgun Gothic", 10))
                
                # 일정 있는 날짜 점 표시 (간단히 배경색 변경 또는 텍스트 추가)
                sched = self.dm.get_schedule(date_str)
                if sched["type"]:
                    if sched["type"] == "8 면": bg_color = "#fadbd8"
                    elif sched["type"] == "1 면": bg_color = "#d1f2eb"
                    elif sched["type"] == "2 면": bg_color = "#fcf3cf"
                
                btn.config(bg=bg_color, fg=fg_color)
                
                # 클릭 이벤트 바인딩
                cmd = lambda d=date_str: self.select_date(d)
                btn.config(command=cmd)
                
                day_count += 1
    
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
    
    def go_today(self):
        self.current_date = datetime.date.today()
        self.update_calendar()
        self.select_date(self.current_date.strftime("%Y-%m-%d"))
    
    def select_date(self, date_str):
        self.selected_date = date_str
        self.lbl_selected_date.config(text=date_str)
        self.load_selected_date_info()
    
    def load_selected_date_info(self):
        if not self.selected_date:
            return
        
        sched = self.dm.get_schedule(self.selected_date)
        
        # 콤보박스 설정
        m_type = sched["type"] if sched["type"] else "없음"
        self.combo_type.set(m_type)
        
        # 사유 입력
        self.entry_reason.delete(0, tk.END)
        self.entry_reason.insert(0, sched.get("reason", ""))
        
        # 메모 입력
        self.text_memo.delete("1.0", tk.END)
        self.text_memo.insert("1.0", sched.get("memo", ""))
        
        # 할 일 로드
        self.refresh_todo_list()
    
    def on_type_change(self, event):
        self.save_schedule()
    
    def save_schedule(self):
        if not self.selected_date:
            return
        
        m_type = self.combo_type.get()
        if m_type == "없음":
            m_type = None
        
        reason = self.entry_reason.get()
        memo = self.text_memo.get("1.0", tk.END).strip()
        
        if m_type or reason or memo:
            self.dm.set_schedule(self.selected_date, m_type, reason, memo)
            self.update_calendar() # 캘린더 색상 업데이트용
        else:
            # 모든 게 비어있으면 삭제 처리 (옵션)
            if self.selected_date in self.dm.data["schedules"]:
                del self.dm.data["schedules"][self.selected_date]
                self.dm.save_data()
                self.update_calendar()
    
    def refresh_todo_list(self):
        self.todo_listbox.delete(0, tk.END)
        todos = self.dm.get_todos(self.selected_date)
        for i, todo in enumerate(todos):
            status = "✅" if todo["done"] else "⬜"
            text = f"{status} {todo['text']}"
            if todo["done"]:
                self.todo_listbox.insert(tk.END, text)
                self.todo_listbox.itemconfig(i, fg='gray')
            else:
                self.todo_listbox.insert(tk.END, text)
                self.todo_listbox.itemconfig(i, fg='black')
    
    def add_todo_item(self):
        text = self.entry_todo.get().strip()
        if text:
            self.dm.add_todo(self.selected_date, text)
            self.entry_todo.delete(0, tk.END)
            self.refresh_todo_list()
    
    def toggle_todo_item(self, event):
        selection = self.todo_listbox.curselection()
        if selection:
            index = selection[0]
            self.dm.toggle_todo(self.selected_date, index)
            self.refresh_todo_list()
    
    def delete_todo_item(self):
        selection = self.todo_listbox.curselection()
        if selection:
            index = selection[0]
            self.dm.delete_todo(self.selected_date, index)
            self.refresh_todo_list()
    
    def set_alarm(self):
        # 간단한 알람 설정 다이얼로그
        top = tk.Toplevel(self.root)
        top.title("알람 설정")
        top.geometry("300x150")
        top.resizable(False, False)
        
        tk.Label(top, text="시간 (HH:MM):", font=("Malgun Gothic", 11)).pack(pady=10)
        entry_time = tk.Entry(top, font=("Consolas", 14), justify='center')
        entry_time.pack()
        entry_time.insert(0, "08:00")
        
        tk.Label(top, text="메시지:", font=("Malgun Gothic", 11)).pack(pady=5)
        entry_msg = tk.Entry(top, width=30)
        entry_msg.pack()
        entry_msg.insert(0, "면학 시간 확인!")
        
        def save():
            t = entry_time.get()
            m = entry_msg.get()
            if len(t) == 5 and t[2] == ':':
                self.dm.add_alarm(t, m)
                self.update_alarm_status()
                messagebox.showinfo("완료", "알람이 등록되었습니다.")
                top.destroy()
            else:
                messagebox.showerror("오류", "시간 형식이 올바르지 않습니다 (HH:MM).")
        
        tk.Button(top, text="등록", command=save, bg=self.colors["primary"], fg="white").pack(pady=10)
    
    def update_alarm_status(self):
        alarms = self.dm.get_alarms()
        count = len(alarms)
        if count > 0:
            self.lbl_alarm_status.config(text=f"등록된 알람: {count}개", fg="blue")
        else:
            self.lbl_alarm_status.config(text="등록된 알람 없음", fg="#7f8c8d")
    
    def sync_desktop(self):
        """선택한 날짜의 정보를 바탕화면 txt 파일로 저장"""
        try:
            desktop = Path.home() / "Desktop"
            filename = f"면학_계획_{self.selected_date}.txt"
            filepath = desktop / filename
            
            sched = self.dm.get_schedule(self.selected_date)
            todos = self.dm.get_todos(self.selected_date)
            
            content = f"[면학 계획] {self.selected_date}\n\n"
            content += f"구분: {sched['type'] if sched['type'] else '없음'}\n"
            content += f"사유: {sched.get('reason', '')}\n"
            content += f"메모: {sched.get('memo', '')}\n\n"
            content += "--- 할 일 목록 ---\n"
            for i, t in enumerate(todos, 1):
                status = "O" if t['done'] else "X"
                content += f"{i}. [{status}] {t['text']}\n"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            messagebox.showinfo("동기화 완료", f"바탕화면에 '{filename}' 이 생성되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"파일 생성 실패: {str(e)}")
    
    def start_alarm_checker(self):
        def check():
            now = datetime.datetime.now()
            current_time_str = now.strftime("%H:%M")
            current_sec = now.second
            
            # 매 정각 0 초에만 확인 (중복 방지)
            if current_sec == 0:
                alarms = self.dm.get_alarms()
                for alarm in alarms:
                    if alarm["active"] and alarm["time"] == current_time_str:
                        self.trigger_alarm(alarm["message"])
                        # 한번 울리면 비활성화 (또는 반복 로직 구현 가능)
                        # 여기서는 한번 울리면 끄는 것으로 설정
                        idx = self.dm.data["alarms"].index(alarm)
                        self.dm.data["alarms"][idx]["active"] = False
                        self.dm.save_data()
                        self.update_alarm_status()
            
            self.root.after(1000, check)
        
        # 시계 업데이트 루프도 여기에 통합
        def update_clock():
            now = datetime.datetime.now()
            self.clock_label.config(text=now.strftime("%Y-%m-%d %H:%M:%S"))
            self.root.after(1000, update_clock)
        
        update_clock()
        check()
    
    def trigger_alarm(self, message):
        # 경고음 재생
        try:
            winsound.Beep(1000, 500) # 1kHz, 0.5 초
            winsound.Beep(1000, 500)
            winsound.Beep(1000, 500)
        except Exception:
            pass # 사운드 오류 무시
        
        # 팝업
        messagebox.showwarning("⏰ 면학 알람", f"{message}\n\n지금 확인하세요!")

if __name__ == "__main__":
    root = tk.Tk()
    # 고딕 폰트 강제 적용 (Windows 환경 고려)
    try:
        root.option_add("*Font", "Malgun Gothic 10")
    except:
        pass
    
    app = MyeonhakApp(root)
    root.mainloop()
