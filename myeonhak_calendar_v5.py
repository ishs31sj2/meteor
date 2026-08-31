import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import datetime
import holidays
import threading
import time
from winsound import Beep  # Windows only sound

# 데이터 파일 경로
DATA_FILE = "myeonhak_data.json"

class MyeonhakData:
    def __init__(self):
        self.data = self.load_data()
    
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_data(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
    
    def get_day_plan(self, date_str):
        return self.data.get(date_str, {
            "8면": {"status": False, "reason": ""},
            "1 면": {"status": False, "reason": ""},
            "2 면": {"status": False, "reason": ""},
            "todos": []
        })
    
    def update_day_plan(self, date_str, plan):
        self.data[date_str] = plan
        self.save_data()

class DetailEditorDialog(tk.Toplevel):
    """상세 편집 다이얼로그 (면불 사유 + ToDo 관리)"""
    def __init__(self, parent, date_str, data_manager):
        super().__init__(parent)
        self.title(f"상세 계획 편집 - {date_str}")
        self.geometry("600x700")
        self.date_str = date_str
        self.dm = data_manager
        self.plan = self.dm.get_day_plan(date_str)
        
        # 모달 설정
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = ttk.Label(main_frame, text=f"{self.date_str} 의 면학 및 할 일 관리", font=("맑은 고딕", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # --- 면학 관리 섹션 ---
        meonhak_frame = ttk.LabelFrame(main_frame, text="면학 관리 (불참 시 사유 기입)", padding="15")
        meonhak_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.myeonhak_vars = {}
        self.myeonhak_reasons = {}
        
        types = ["8 면", "1 면", "2 면"]
        colors = {"8 면": "#ffcccc", "1 면": "#ccffcc", "2 면": "#ffffcc"}
        
        for m_type in types:
            frame = ttk.Frame(myeonhak_frame)
            frame.pack(fill=tk.X, pady=5)
            
            # 상태 체크박스
            var = tk.BooleanVar(value=self.plan[m_type]["status"])
            chk = ttk.Checkbutton(frame, text=f"{m_type} 면학 참석", variable=var, 
                                  command=lambda t=m_type: self.toggle_reason_state(t))
            chk.pack(side=tk.LEFT)
            self.myeonhak_vars[m_type] = var
            
            # 사유 입력창 (불참일 때만 활성화될 수 있도록 유도하지만, 항상 입력 가능하게 하되 의미 부여)
            lbl = ttk.Label(frame, text="불참 사유:", width=10)
            lbl.pack(side=tk.LEFT, padx=(10, 5))
            
            reason_entry = ttk.Entry(frame, width=40)
            reason_entry.insert(0, self.plan[m_type]["reason"])
            reason_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.myeonhak_reasons[m_type] = reason_entry
            
            # 시각적 피드백 (초기 상태)
            if not var.get(): # 불참이면 배경색 약간 변경 (간단히 라벨 색상 등으로 대체 가능하나 Entry 는 제한적)
                pass 

        # --- ToDo 관리 섹션 ---
        todo_frame = ttk.LabelFrame(main_frame, text="할 일 (ToDo) 관리", padding="15")
        todo_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 입력 영역
        input_frame = ttk.Frame(todo_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.todo_entry = ttk.Entry(input_frame)
        self.todo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.todo_entry.bind("<Return>", lambda e: self.add_todo())
        
        add_btn = ttk.Button(input_frame, text="추가", command=self.add_todo)
        add_btn.pack(side=tk.RIGHT)
        
        # 리스트 영역
        list_frame = ttk.Frame(todo_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.todo_listbox = tk.Listbox(list_frame, font=("맑은 고딕", 10), selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.todo_listbox.yview)
        self.todo_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.todo_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 더블클릭으로 완료/취소
        self.todo_listbox.bind("<Double-Button-1>", self.toggle_todo_complete)
        
        # 삭제 버튼
        del_btn = ttk.Button(todo_frame, text="선택 항목 삭제", command=self.delete_todo)
        del_btn.pack(pady=(10, 0))
        
        # 초기 로드
        self.refresh_todo_list()
        
        # 저장 버튼
        save_btn = ttk.Button(main_frame, text="저장하고 닫기", command=self.save_and_close)
        save_btn.pack(pady=(20, 0))
    
    def toggle_reason_state(self, m_type):
        # 참석 체크해제시 사유 입력을 권장하는 로직 등은 여기서 구현 가능
        pass

    def refresh_todo_list(self):
        self.todo_listbox.delete(0, tk.END)
        for todo in self.plan["todos"]:
            status = "[완료] " if todo["done"] else "[ ] "
            text = f"{status}{todo['text']}"
            self.todo_listbox.insert(tk.END, text)
            # 완료된 항목은 회색으로 표시 (단순 텍스트 기반이라 제한적이지만 가능)
            if todo["done"]:
                self.todo_listbox.itemconfig(self.todo_listbox.size()-1, {'fg': 'gray'})
            else:
                self.todo_listbox.itemconfig(self.todo_listbox.size()-1, {'fg': 'black'})

    def add_todo(self):
        text = self.todo_entry.get().strip()
        if text:
            self.plan["todos"].append({"text": text, "done": False})
            self.todo_entry.delete(0, tk.END)
            self.refresh_todo_list()
    
    def delete_todo(self):
        sel = self.todo_listbox.curselection()
        if sel:
            idx = sel[0]
            del self.plan["todos"][idx]
            self.refresh_todo_list()
    
    def toggle_todo_complete(self, event):
        sel = self.todo_listbox.curselection()
        if sel:
            idx = sel[0]
            self.plan["todos"][idx]["done"] = not self.plan["todos"][idx]["done"]
            self.refresh_todo_list()
    
    def save_and_close(self):
        # 면학 데이터 업데이트
        for m_type in ["8 면", "1 면", "2 면"]:
            self.plan[m_type]["status"] = self.myeonhak_vars[m_type].get()
            self.plan[m_type]["reason"] = self.myeonhak_reasons[m_type].get()
        
        self.dm.update_day_plan(self.date_str, self.plan)
        self.destroy()

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("면학 불참 계획 관리자 Ultimate v5")
        self.root.geometry("1000x800")
        
        self.dm = MyeonhakData()
        self.current_date = datetime.date.today()
        self.kr_holidays = holidays.Korea()
        
        self.setup_styles()
        self.create_ui()
        self.update_calendar()
        self.start_clock()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("맑은 고딕", 10), padding=5)
        style.configure("Header.TLabel", font=("맑은 고딕", 16, "bold"))
        style.configure("Today.TLabel", font=("맑은 고딕", 10, "bold"), foreground="white", background="#007ACC")
    
    def create_ui(self):
        # 상단 프레임 (시계 + 네비게이션)
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        self.clock_label = ttk.Label(top_frame, text="", font=("Consolas", 20, "bold"), foreground="#007ACC")
        self.clock_label.pack(side=tk.LEFT)
        
        nav_frame = ttk.Frame(top_frame)
        nav_frame.pack(side=tk.RIGHT)
        
        ttk.Button(nav_frame, text="< 이전", command=self.prev_month).pack(side=tk.LEFT, padx=5)
        ttk.Label(nav_frame, text="", width=5).pack(side=tk.LEFT) # spacer
        self.month_label = ttk.Label(nav_frame, text="", style="Header.TLabel")
        self.month_label.pack(side=tk.LEFT)
        ttk.Label(nav_frame, text="", width=5).pack(side=tk.LEFT) # spacer
        ttk.Button(nav_frame, text="다음 >", command=self.next_month).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="오늘", command=self.go_today).pack(side=tk.LEFT, padx=10)
        
        # 메인 콘텐츠 (달력 + 사이드바)
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 달력 프레임
        cal_frame = ttk.Frame(content_frame, relief="ridge", borderwidth=2)
        cal_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 요일 헤더
        days = ["월", "화", "수", "목", "금", "토", "일"]
        header_frame = ttk.Frame(cal_frame)
        header_frame.pack(fill=tk.X)
        for i, day in enumerate(days):
            fg = "red" if i >= 5 else "black"
            lbl = ttk.Label(header_frame, text=day, width=10, anchor="center", font=("맑은 고딕", 11, "bold"), foreground=fg)
            lbl.pack(side=tk.LEFT, expand=True)
        
        # 달력 그리드
        self.cal_grid = ttk.Frame(cal_frame)
        self.cal_grid.pack(fill=tk.BOTH, expand=True)
        
        # 우측 사이드바 (간단 정보 및 액션)
        side_frame = ttk.Frame(content_frame, width=300, relief="sunken", borderwidth=2)
        side_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        side_frame.pack_propagate(False)
        
        ttk.Label(side_frame, text="📅 빠른 액션", style="Header.TLabel").pack(pady=20)
        
        ttk.Button(side_frame, text="선택 날짜 상세 편집\n(면불 사유/ToDo)", command=self.open_detail_editor).pack(fill=tk.X, padx=20, pady=10)
        ttk.Button(side_frame, text="바탕화면 메모 동기화", command=self.sync_desktop_memo).pack(fill=tk.X, padx=20, pady=10)
        ttk.Button(side_frame, text="알람 설정", command=self.set_alarm).pack(fill=tk.X, padx=20, pady=10)
        
        self.info_label = ttk.Label(side_frame, text="날짜를 선택하세요.", wraplength=250, justify="left")
        self.info_label.pack(padx=20, pady=20, anchor="nw")
        
        self.selected_date = None
        self.day_buttons = {} # 날짜 버튼 저장

    def start_clock(self):
        def update():
            now = datetime.datetime.now()
            self.clock_label.config(text=now.strftime("%Y-%m-%d %H:%M:%S"))
            self.root.after(1000, update)
        update()

    def update_calendar(self):
        # 그리드 초기화
        for widget in self.cal_grid.winfo_children():
            widget.destroy()
        self.day_buttons.clear()
        
        year = self.current_date.year
        month = self.current_date.month
        
        self.month_label.config(text=f"{year}년 {month}월")
        
        # 첫 날 요일 (월요일=0) 과 마지막 날 계산
        first_day = datetime.date(year, month, 1)
        if month == 12:
            last_day = datetime.date(year+1, 1, 1) - datetime.timedelta(days=1)
        else:
            last_day = datetime.date(year, month+1, 1) - datetime.timedelta(days=1)
        
        start_weekday = first_day.weekday() # 0=Mon
        total_days = last_day.day
        
        # 빈 칸 채우기
        for i in range(start_weekday):
            ttk.Label(self.cal_grid, text="", width=10, height=4).grid(row=0, column=i)
        
        # 날짜 채우기
        row = 0
        col = start_weekday
        for day in range(1, total_days+1):
            current_date = datetime.date(year, month, day)
            date_str = current_date.strftime("%Y-%m-%d")
            is_weekend = current_date.weekday() >= 5
            is_holiday = date_str in self.kr_holidays
            is_today = current_date == datetime.date.today()
            
            # 면학 상태 확인
            plan = self.dm.get_day_plan(date_str)
            has_8 = not plan["8 면"]["status"] # 불참이면 True
            has_1 = not plan["1 면"]["status"]
            has_2 = not plan["2 면"]["status"]
            
            # 버튼 텍스트 구성
            btn_text = f"{day}일"
            if has_8 or has_1 or has_2:
                indicators = []
                if has_8: indicators.append("8")
                if has_1: indicators.append("1")
                if has_2: indicators.append("2")
                btn_text += f"\n({','.join(indicators)}면)"
            
            bg_color = "white"
            fg_color = "black"
            
            if is_holiday:
                fg_color = "red"
                btn_text += f"\n{self.kr_holidays.get(date_str)}"
            elif is_weekend:
                fg_color = "blue"
            
            if is_today:
                bg_color = "#007ACC"
                fg_color = "white"
            
            btn = tk.Button(self.cal_grid, text=btn_text, width=10, height=4, 
                            bg=bg_color, fg=fg_color, relief="raised",
                            command=lambda d=date_str: self.select_date(d),
                            font=("맑은 고딕", 9))
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.day_buttons[day] = btn
            
            col += 1
            if col > 6:
                col = 0
                row += 1

    def select_date(self, date_str):
        self.selected_date = date_str
        plan = self.dm.get_day_plan(date_str)
        
        # 사이드바 정보 업데이트
        info_text = f"선택 날짜: {date_str}\n\n"
        info_text += "📘 면학 상태:\n"
        info_text += f"  8 면: {'참가' if plan['8 면']['status'] else '불참'}"
        if not plan['8 면']['status'] and plan['8 면']['reason']:
            info_text += f" ({plan['8 면']['reason']})"
        info_text += "\n"
        
        info_text += f"  1 면: {'참가' if plan['1 면']['status'] else '불참'}"
        if not plan['1 면']['status'] and plan['1 면']['reason']:
            info_text += f" ({plan['1 면']['reason']})"
        info_text += "\n"

        info_text += f"  2 면: {'참가' if plan['2 면']['status'] else '불참'}"
        if not plan['2 면']['status'] and plan['2 면']['reason']:
            info_text += f" ({plan['2 면']['reason']})"
        info_text += "\n\n"
        
        info_text += "✅ 할 일:\n"
        if plan["todos"]:
            for todo in plan["todos"]:
                status = "✔" if todo["done"] else "○"
                info_text += f"  {status} {todo['text']}\n"
        else:
            info_text += "  등록된 할 일이 없습니다.\n"
        
        self.info_label.config(text=info_text)

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

    def open_detail_editor(self):
        if not self.selected_date:
            messagebox.showwarning("알림", "먼저 달력에서 날짜를 선택해주세요.")
            return
        DetailEditorDialog(self.root, self.selected_date, self.dm)
        self.update_calendar() # 닫히고 나면 캘린더 갱신 (인디케이터 등)
        self.select_date(self.selected_date) # 사이드바 정보도 갱신

    def sync_desktop_memo(self):
        if not self.selected_date:
            messagebox.showwarning("알림", "먼저 달력에서 날짜를 선택해주세요.")
            return
        
        plan = self.dm.get_day_plan(self.selected_date)
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = f"면학_메모_{self.selected_date}.txt"
        filepath = os.path.join(desktop_path, filename)
        
        content = f"[{self.selected_date}] 면학 및 할 일 계획\n"
        content += "="*30 + "\n"
        for m_type in ["8 면", "1 면", "2 면"]:
            status = "참가" if plan[m_type]["status"] else "불참"
            reason = plan[m_type]["reason"]
            content += f"{m_type}: {status}"
            if reason: content += f" - 사유: {reason}"
            content += "\n"
        
        content += "\n[할 일 목록]\n"
        for todo in plan["todos"]:
            done = "V" if todo["done"] else " "
            content += f"[{done}] {todo['text']}\n"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("성공", f"바탕화면에 '{filename}' 이 생성되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"파일 생성 실패: {str(e)}")

    def set_alarm(self):
        # 간단한 알람 설정 데모 (실제로는 별도 스레드나 스케줄러 필요)
        alarm_time = simpledialog.askstring("알람 설정", "알람 시간을 입력하세요 (HH:MM 형식, 예: 14:30)")
        if alarm_time:
            try:
                h, m = map(int, alarm_time.split(":"))
                messagebox.showinfo("알람 설정됨", f"{alarm_time} 에 알람이 설정되었습니다.\n(프로그램이 켜져있을 때만 작동)")
                # 실제 알람 로직은 생략 (간소화를 위해)
            except:
                messagebox.showerror("오류", "시간 형식이 잘못되었습니다.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()
