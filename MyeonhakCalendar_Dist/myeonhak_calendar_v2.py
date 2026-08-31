import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import json
import os
import calendar
import webbrowser

# 데이터 파일 경로
DATA_FILE = "myeonhak_data.json"

class DataManager:
    def __init__(self):
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"schedules": {}, "todos": {}, "holidays": []}
        return {"schedules": {}, "todos": {}, "holidays": []}

    def save_data(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def get_date_key(self, date_obj):
        return date_obj.strftime("%Y-%m-%d")

    def add_schedule(self, date_str, session_type, status, memo=""):
        if date_str not in self.data["schedules"]:
            self.data["schedules"][date_str] = []
        
        # 기존 중복 제거 (같은 세션은 업데이트)
        self.data["schedules"][date_str] = [
            s for s in self.data["schedules"][date_str] if s["type"] != session_type
        ]
        
        self.data["schedules"][date_str].append({
            "type": session_type,
            "status": status,
            "memo": memo,
            "updated_at": datetime.now().isoformat()
        })
        self.save_data()

    def add_todo(self, date_str, content, is_done=False):
        if date_str not in self.data["todos"]:
            self.data["todos"][date_str] = []
        self.data["todos"][date_str].append({
            "content": content,
            "done": is_done
        })
        self.save_data()

    def toggle_todo(self, date_str, index):
        if date_str in self.data["todos"] and 0 <= index < len(self.data["todos"][date_str]):
            self.data["todos"][date_str][index]["done"] = not self.data["todos"][date_str][index]["done"]
            self.save_data()

    def delete_todo(self, date_str, index):
        if date_str in self.data["todos"] and 0 <= index < len(self.data["todos"][date_str]):
            del self.data["todos"][date_str][index]
            self.save_data()

    def get_schedules(self, date_str):
        return self.data["schedules"].get(date_str, [])

    def get_todos(self, date_str):
        return self.data["todos"].get(date_str, [])

    def is_holiday(self, date_str):
        # 간단한 공휴일 체크 (사용자가 추가한 것 기준)
        # 실제 공휴일 API 연동은 복잡하므로 여기서는 수동 등록 기반으로 하거나 기본 공휴일 리스트 활용
        weekends = ["Sat", "Sun"]
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        if dt.strftime("%a") in weekends:
            return True
        return False

class ModernCalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("면학 불참 계획 관리자")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 데이터 매니저 초기화
        self.dm = DataManager()
        
        # 현재 날짜 설정
        self.current_date = datetime.now()
        self.view_mode = "month" # day, week, month, year
        
        # 스타일 설정
        self.setup_styles()
        
        # UI 구성
        self.create_header()
        self.create_main_layout()
        
        # 초기 렌더링
        self.render_calendar()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # 색상 팔레트
        self.colors = {
            "bg": "#1e1e1e",
            "fg": "#ffffff",
            "panel_bg": "#2d2d2d",
            "accent": "#007acc",
            "accent_hover": "#005f9e",
            "text_disabled": "#aaaaaa",
            "border": "#3e3e3e",
            "8면": "#ff6b6b",
            "1면": "#4ecdc4",
            "2면": "#ffe66d",
            "공휴일": "#95a5a6",
            "시험": "#ff9f43",
            "완료": "#2ecc71"
        }
        
        self.root.configure(bg=self.colors["bg"])
        
        # 버튼 스타일
        style.configure("TButton", 
            background=self.colors["accent"], 
            foreground="white", 
            borderwidth=0, 
            focusthickness=0, 
            padding=10)
        style.map("TButton", background=[("active", self.colors["accent_hover"])])
        
        # 라벨 스타일
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["fg"], font=("Malgun Gothic", 10))
        style.configure("Header.TLabel", font=("Malgun Gothic", 16, "bold"))
        style.configure("DayName.TLabel", font=("Malgun Gothic", 10, "bold"), foreground=self.colors["text_disabled"])

    def create_header(self):
        header_frame = tk.Frame(self.root, bg=self.colors["panel_bg"], height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        # 네비게이션 버튼
        btn_prev = tk.Button(header_frame, text="<", command=self.prev_period, bg=self.colors["panel_bg"], fg="white", font=("Arial", 12, "bold"), bd=0, cursor="hand2")
        btn_prev.pack(side=tk.LEFT, padx=20, pady=15)
        
        self.lbl_current_period = tk.Label(header_frame, text="", bg=self.colors["panel_bg"], fg="white", font=("Malgun Gothic", 18, "bold"))
        self.lbl_current_period.pack(side=tk.LEFT, expand=True)
        
        btn_next = tk.Button(header_frame, text=">", command=self.next_period, bg=self.colors["panel_bg"], fg="white", font=("Arial", 12, "bold"), bd=0, cursor="hand2")
        btn_next.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # 뷰 모드 변경 버튼
        mode_frame = tk.Frame(header_frame, bg=self.colors["panel_bg"])
        mode_frame.pack(side=tk.RIGHT, padx=20)
        
        modes = ["주", "월", "년"]
        for i, mode in enumerate(modes):
            btn = tk.Button(mode_frame, text=mode, command=lambda m=mode: self.change_view(m), 
                            bg=self.colors["accent"] if self.view_mode == ["week", "month", "year"][i] else self.colors["panel_bg"],
                            fg="white", bd=0, padx=15, pady=5, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=2)
            # 단순화를 위해 여기서는 월 뷰만 완전히 구현하고 주/년은 알림 표시
            if mode != "월":
                btn.config(command=lambda m=mode: messagebox.showinfo("알림", "현재 버전에서는 '월' 뷰만 지원합니다. 추후 업데이트 예정."))

        # 오늘 버튼
        btn_today = tk.Button(header_frame, text="오늘", command=self.go_to_today, bg="#444444", fg="white", bd=0, padx=15, pady=5, cursor="hand2")
        btn_today.pack(side=tk.RIGHT, padx=10)

    def create_main_layout(self):
        main_container = tk.Frame(self.root, bg=self.colors["bg"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 왼쪽: 달력 영역
        self.calendar_frame = tk.Frame(main_container, bg=self.colors["panel_bg"], highlightthickness=0)
        self.calendar_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 오른쪽: 상세 정보 및 할 일 영역
        self.detail_frame = tk.Frame(main_container, bg=self.colors["panel_bg"], width=300)
        self.detail_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        self.detail_frame.pack_propagate(False)
        
        self.lbl_selected_date = tk.Label(self.detail_frame, text="날짜 선택", bg=self.colors["panel_bg"], fg="white", font=("Malgun Gothic", 14, "bold"))
        self.lbl_selected_date.pack(pady=20, padx=20, anchor="w")
        
        # 면학 계획 섹션
        tk.Label(self.detail_frame, text="📚 면학 계획", bg=self.colors["panel_bg"], fg=self.colors["text_disabled"], font=("Malgun Gothic", 11, "bold")).pack(padx=20, anchor="w")
        self.schedule_listbox = tk.Listbox(self.detail_frame, bg="#333333", fg="white", selectbackground=self.colors["accent"], selectforeground="white", borderwidth=0, highlightthickness=0, font=("Malgun Gothic", 10))
        self.schedule_listbox.pack(fill=tk.X, padx=20, pady=10)
        
        btn_add_schedule = tk.Button(self.detail_frame, text="+ 면학 계획 추가", command=self.add_schedule_dialog, bg="#333333", fg=self.colors["accent"], bd=0, pady=5, cursor="hand2", font=("Malgun Gothic", 9))
        btn_add_schedule.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # 할 일 섹션
        tk.Label(self.detail_frame, text="✅ 할 일 목록", bg=self.colors["panel_bg"], fg=self.colors["text_disabled"], font=("Malgun Gothic", 11, "bold")).pack(padx=20, anchor="w")
        
        self.todo_frame = tk.Frame(self.detail_frame, bg=self.colors["panel_bg"])
        self.todo_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.entry_todo = tk.Entry(self.todo_frame, bg="#333333", fg="white", insertbackground="white", borderwidth=0, highlightthickness=1, highlightbackground="#555555", font=("Malgun Gothic", 10))
        self.entry_todo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_todo.bind("<Return>", lambda e: self.add_todo())
        
        btn_add_todo = tk.Button(self.todo_frame, text="+", command=self.add_todo, bg=self.colors["accent"], fg="white", bd=0, width=3, cursor="hand2")
        btn_add_todo.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.todo_list_frame = tk.Frame(self.detail_frame, bg=self.colors["panel_bg"])
        self.todo_list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(self.todo_list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.todo_listbox = tk.Listbox(self.todo_list_frame, bg="#333333", fg="white", selectbackground=self.colors["accent"], selectforeground="white", borderwidth=0, highlightthickness=0, font=("Malgun Gothic", 10), yscrollcommand=scrollbar.set)
        self.todo_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.todo_listbox.yview)
        
        self.todo_listbox.bind("<Double-Button-1>", self.toggle_todo_status)
        self.todo_listbox.bind("<Delete>", lambda e: self.delete_todo())
        
        btn_del_todo = tk.Button(self.detail_frame, text="선택 항목 삭제", command=self.delete_todo, bg="#c0392b", fg="white", bd=0, pady=5, cursor="hand2", font=("Malgun Gothic", 9))
        btn_del_todo.pack(fill=tk.X, padx=20, pady=(0, 10))

    def render_calendar(self):
        # 기존 위젯 정리
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
            
        year = self.current_date.year
        month = self.current_date.month
        
        self.lbl_current_period.config(text=f"{year}년 {month}월")
        
        # 요일 헤더
        days_kr = ["월", "화", "수", "목", "금", "토", "일"]
        header_frame = tk.Frame(self.calendar_frame, bg=self.colors["panel_bg"])
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        for i, day in enumerate(days_kr):
            color = "#ff6b6b" if i >= 5 else self.colors["text_disabled"]
            lbl = tk.Label(header_frame, text=day, bg=self.colors["panel_bg"], fg=color, font=("Malgun Gothic", 11, "bold"), width=10)
            lbl.grid(row=0, column=i, padx=2, pady=5)
            
        # 날짜 그리드
        grid_frame = tk.Frame(self.calendar_frame, bg=self.colors["panel_bg"])
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 첫 날의 요일과 전체 날짜 수 계산
        first_day_weekday, num_days = calendar.monthrange(year, month)
        # calendar.monthrange 는 월요일을 0 으로 반환하지만, 우리 배열은 월요일이 0 이므로 맞음.
        # 단, calendar 모듈은 월요일=0 ... 일요일=6
        
        start_offset = first_day_weekday # 0=Mon, 6=Sun
        
        current_day = 1
        rows = (num_days + start_offset + 6) // 7
        
        for r in range(rows):
            row_frame = tk.Frame(grid_frame, bg=self.colors["panel_bg"])
            row_frame.pack(fill=tk.X, expand=True)
            for c in range(7):
                cell_frame = tk.Frame(row_frame, bg="#333333", highlightthickness=1, highlightbackground="#444444")
                cell_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)
                
                if r == 0 and c < start_offset:
                    continue
                
                if current_day > num_days:
                    break
                
                date_obj = datetime(year, month, current_day)
                date_str = date_obj.strftime("%Y-%m-%d")
                is_weekend = c >= 5
                is_today = (date_obj.day == datetime.now().day and 
                            date_obj.month == datetime.now().month and 
                            date_obj.year == datetime.now().year)
                
                # 날짜 숫자 레이블
                day_num_color = "#ff6b6b" if is_weekend else ("#fff" if not is_weekend else "#ddd")
                if is_today:
                    day_num_color = "#000"
                
                lbl_day = tk.Label(cell_frame, text=str(current_day), bg="#333333" if not is_today else self.colors["accent"], 
                                   fg=day_num_color if not is_today else "white", 
                                   font=("Malgun Gothic", 12, "bold" if is_today else "normal"),
                                   anchor="nw", padx=5, pady=5)
                lbl_day.pack(fill=tk.X)
                
                # 작은 인디케이터 (면학 여부)
                schedules = self.dm.get_schedules(date_str)
                indicator_text = ""
                colors = []
                for s in schedules:
                    if s["status"] == "불참":
                        indicator_text += "■ "
                        colors.append(self.colors.get(s["type"], "#fff"))
                
                if indicator_text:
                    lbl_ind = tk.Label(cell_frame, text=indicator_text.strip(), bg="#333333", fg=colors[0] if colors else "#fff", font=("Arial", 8), anchor="sw", padx=5, pady=2)
                    lbl_ind.pack(fill=tk.X, side=tk.BOTTOM)
                
                # 클릭 이벤트
                cell_frame.bind("<Button-1>", lambda e, d=date_str: self.on_date_click(d))
                lbl_day.bind("<Button-1>", lambda e, d=date_str: self.on_date_click(d))
                if indicator_text:
                    lbl_ind.bind("<Button-1>", lambda e, d=date_str: self.on_date_click(d))
                
                current_day += 1

    def on_date_click(self, date_str):
        self.selected_date = date_str
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        self.lbl_selected_date.config(text=f"{dt.year}년 {dt.month}월 {dt.day}일 ({['월','화','수','목','금','토','일'][dt.weekday()]})")
        self.refresh_detail_view()

    def refresh_detail_view(self):
        if not hasattr(self, 'selected_date'):
            return
            
        date_str = self.selected_date
        
        # 면학 목록 업데이트
        self.schedule_listbox.delete(0, tk.END)
        schedules = self.dm.get_schedules(date_str)
        if not schedules:
            self.schedule_listbox.insert(tk.END, "등록된 면학 계획이 없습니다.")
        else:
            for s in schedules:
                status_icon = "❌" if s["status"] == "불참" else "⭕"
                text = f"{status_icon} {s['type']} ({s['status']})"
                if s.get("memo"):
                    text += f" - {s['memo']}"
                self.schedule_listbox.insert(tk.END, text)
        
        # 할 일 목록 업데이트
        self.todo_listbox.delete(0, tk.END)
        todos = self.dm.get_todos(date_str)
        for i, t in enumerate(todos):
            prefix = "✅" if t["done"] else "⬜"
            style_str = "strike" if t["done"] else "normal"
            self.todo_listbox.insert(tk.END, f"{prefix} {t['content']}")
            if t["done"]:
                self.todo_listbox.itemconfig(i, fg='#888888')

    def add_schedule_dialog(self):
        if not hasattr(self, 'selected_date'):
            messagebox.showwarning("알림", "먼저 날짜를 선택해주세요.")
            return
            
        # 간단한 커스텀 다이얼로그 대신 입력 받기
        top = tk.Toplevel(self.root)
        top.title("면학 계획 추가")
        top.geometry("300x250")
        top.configure(bg=self.colors["panel_bg"])
        top.resizable(False, False)
        
        tk.Label(top, text="면학 종류", bg=self.colors["panel_bg"], fg="white").pack(pady=10)
        type_var = tk.StringVar(value="8면")
        ttk.Combobox(top, textvariable=type_var, values=["8면", "1면", "2면"], state="readonly").pack(fill=tk.X, padx=20)
        
        tk.Label(top, text="상태", bg=self.colors["panel_bg"], fg="white").pack(pady=10)
        status_var = tk.StringVar(value="불참")
        ttk.Combobox(top, textvariable=status_var, values=["불참", "참가"], state="readonly").pack(fill=tk.X, padx=20)
        
        tk.Label(top, text="비고", bg=self.colors["panel_bg"], fg="white").pack(pady=10)
        memo_entry = tk.Entry(top, bg="#333333", fg="white")
        memo_entry.pack(fill=tk.X, padx=20)
        
        def save():
            self.dm.add_schedule(self.selected_date, type_var.get(), status_var.get(), memo_entry.get())
            self.refresh_detail_view()
            self.render_calendar() # 인디케이터 업데이트
            top.destroy()
            
        tk.Button(top, text="저장", command=save, bg=self.colors["accent"], fg="white").pack(pady=20)

    def add_todo(self):
        if not hasattr(self, 'selected_date'):
            return
        content = self.entry_todo.get().strip()
        if content:
            self.dm.add_todo(self.selected_date, content)
            self.entry_todo.delete(0, tk.END)
            self.refresh_detail_view()

    def toggle_todo_status(self, event):
        if not hasattr(self, 'selected_date'):
            return
        selection = self.todo_listbox.curselection()
        if selection:
            index = selection[0]
            self.dm.toggle_todo(self.selected_date, index)
            self.refresh_detail_view()

    def delete_todo(self):
        if not hasattr(self, 'selected_date'):
            return
        selection = self.todo_listbox.curselection()
        if selection:
            index = selection[0]
            self.dm.delete_todo(self.selected_date, index)
            self.refresh_detail_view()

    def prev_period(self):
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.render_calendar()

    def next_period(self):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.render_calendar()

    def change_view(self, mode):
        self.view_mode = mode
        # 향후 확장 가능성预留

    def go_to_today(self):
        self.current_date = datetime.now()
        self.render_calendar()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernCalendarApp(root)
    root.mainloop()
