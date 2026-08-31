#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
면학 불참 계획 관리 프로그램 (달력 UI 버전)
- 주/월/년 뷰 지원
- 평일 월~금: 8면, 1면, 2면 계획 관리
- 공휴일 및 시험 일정 기입
- 데이터 자동 저장 (JSON)
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime, timedelta
from calendar import monthrange, monthcalendar
import holidays

# 데이터 파일 경로
DATA_FILE = "myeonhak_data.json"

class MyeonhakManager:
    def __init__(self, root):
        self.root = root
        self.root.title("면학 불참 계획 관리")
        self.root.geometry("1200x800")
        
        # 현재 날짜 설정
        self.current_date = datetime.now()
        self.current_view = "month"  # 'week', 'month', 'year'
        
        # 데이터 로드
        self.data = self.load_data()
        
        # 한국 공휴일
        self.kr_holidays = holidays.Korea()
        
        # UI 생성
        self.create_ui()
        self.refresh_calendar()
        
    def load_data(self):
        """데이터 로드"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "plans": {},  # key: "YYYY-MM-DD", value: {"8면": bool, "1면": bool, "2면": bool}
            "todos": {},  # key: "YYYY-MM-DD", value: [{"text": str, "done": bool}]
            "events": {}  # key: "YYYY-MM-DD", value: [{"type": "holiday/exam", "text": str}]
        }
    
    def save_data(self):
        """데이터 저장"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def create_ui(self):
        """UI 생성"""
        # 상단 프레임 - 네비게이션
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 년도 표시 및 이동 버튼
        self.year_label = ttk.Label(top_frame, text="", font=("Arial", 16, "bold"))
        self.year_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(top_frame, text="◀", command=self.prev_period).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="▶", command=self.next_period).pack(side=tk.LEFT, padx=5)
        
        # 뷰 전환 버튼
        view_frame = ttk.Frame(top_frame)
        view_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Button(view_frame, text="주", command=lambda: self.set_view("week")).pack(side=tk.LEFT, padx=5)
        ttk.Button(view_frame, text="월", command=lambda: self.set_view("month")).pack(side=tk.LEFT, padx=5)
        ttk.Button(view_frame, text="년", command=lambda: self.set_view("year")).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(top_frame, text="오늘", command=self.go_to_today).pack(side=tk.RIGHT, padx=5)
        
        # 요일 헤더
        self.header_frame = ttk.Frame(self.root)
        self.header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 캘린더 영역
        self.calendar_frame = ttk.Frame(self.root)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 하단 프레임 - 작업 버튼
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(bottom_frame, text="면학 계획 추가", command=self.add_myeonhak_plan).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="할 일 추가", command=self.add_todo).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="이벤트 추가", command=self.add_event).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="선택일 삭제", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="통계 보기", command=self.show_stats).pack(side=tk.RIGHT, padx=5)
        
        # 상태 바
        self.status_var = tk.StringVar(value="준비됨")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def clear_calendar(self):
        """캘린더 초기화"""
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        for widget in self.header_frame.winfo_children():
            widget.destroy()
    
    def refresh_calendar(self):
        """캘린더 새로고침"""
        self.clear_calendar()
        
        if self.current_view == "week":
            self.render_week_view()
        elif self.current_view == "month":
            self.render_month_view()
        elif self.current_view == "year":
            self.render_year_view()
        
        self.update_header()
    
    def update_header(self):
        """헤더 업데이트"""
        if self.current_view == "week":
            start = self.get_week_start()
            end = start + timedelta(days=6)
            self.year_label.config(text=f"{start.year}년 {start.month}월 {start.day}일 - {end.month}월 {end.day}일")
        elif self.current_view == "month":
            self.year_label.config(text=f"{self.current_date.year}년 {self.current_date.month}월")
        else:  # year
            self.year_label.config(text=f"{self.current_date.year}년")
    
    def get_week_start(self):
        """현재 주의 월요일 구하기"""
        return self.current_date - timedelta(days=self.current_date.weekday())
    
    def render_week_view(self):
        """주 뷰 렌더링"""
        start = self.get_week_start()
        
        # 요일 헤더
        days = ["월", "화", "수", "목", "금", "토", "일"]
        for i, day in enumerate(days):
            lbl = ttk.Label(self.header_frame, text=day, font=("Arial", 12, "bold"), width=15, anchor=tk.CENTER)
            lbl.grid(row=0, column=i, padx=2, pady=5)
        
        # 날짜 셀
        for i in range(7):
            date = start + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            is_weekend = date.weekday() >= 5
            
            cell = ttk.Frame(self.calendar_frame, relief=tk.RIDGE, borderwidth=1)
            cell.grid(row=0, column=i, padx=2, pady=2, sticky="nsew")
            
            # 날짜 라벨
            date_lbl = ttk.Label(cell, text=f"{date.month}/{date.day}", font=("Arial", 14, "bold"))
            date_lbl.pack(pady=5)
            
            # 공휴일 표시
            if date_str in self.kr_holidays:
                holiday_name = self.kr_holidays.get(date_str)
                ttk.Label(cell, text=f"🎉 {holiday_name}", foreground="red").pack()
            
            # 이벤트 표시
            if date_str in self.data["events"]:
                for event in self.data["events"][date_str]:
                    color = "red" if event["type"] == "exam" else "blue"
                    ttk.Label(cell, text=f"📌 {event['text']}", foreground=color, font=("Arial", 9)).pack()
            
            # 면학 계획 표시 (평일만)
            if not is_weekend and date_str in self.data["plans"]:
                plans = self.data["plans"][date_str]
                for myeong, active in plans.items():
                    if active:
                        color = "green" if myeong == "8면" else ("orange" if myeong == "1면" else "purple")
                        ttk.Label(cell, text=f"✓ {myeong}", foreground=color).pack()
            
            # 할 일 개수 표시
            if date_str in self.data["todos"]:
                todo_count = len([t for t in self.data["todos"][date_str] if not t["done"]])
                if todo_count > 0:
                    ttk.Label(cell, text=f"📝 할일 {todo_count}개", foreground="gray").pack()
            
            # 클릭 이벤트
            cell.bind("<Button-1>", lambda e, d=date_str: self.on_date_click(d))
            date_lbl.bind("<Button-1>", lambda e, d=date_str: self.on_date_click(d))
            
            self.calendar_frame.grid_columnconfigure(i, weight=1)
    
    def render_month_view(self):
        """월 뷰 렌더링"""
        year = self.current_date.year
        month = self.current_date.month
        
        # 요일 헤더
        days = ["월", "화", "수", "목", "금", "토", "일"]
        for i, day in enumerate(days):
            lbl = ttk.Label(self.header_frame, text=day, font=("Arial", 12, "bold"), width=15, anchor=tk.CENTER)
            lbl.grid(row=0, column=i, padx=2, pady=5)
        
        # 달력 그리드
        cal = monthcalendar(year, month)
        week_num = 0
        
        for week in cal:
            col = 0
            for day in week:
                if day == 0:
                    col += 1
                    continue
                
                date = datetime(year, month, day)
                date_str = date.strftime("%Y-%m-%d")
                is_weekend = date.weekday() >= 5
                
                cell = ttk.Frame(self.calendar_frame, relief=tk.RIDGE, borderwidth=1)
                cell.grid(row=week_num+1, column=col, padx=2, pady=2, sticky="nsew")
                
                # 날짜 라벨
                date_lbl = ttk.Label(cell, text=str(day), font=("Arial", 12, "bold"))
                date_lbl.pack(pady=2)
                
                # 공휴일 표시
                if date_str in self.kr_holidays:
                    holiday_name = self.kr_holidays.get(date_str)
                    ttk.Label(cell, text=f"🎉", foreground="red").pack()
                
                # 이벤트 간략 표시
                if date_str in self.data["events"]:
                    exam_count = len([e for e in self.data["events"][date_str] if e["type"] == "exam"])
                    if exam_count > 0:
                        ttk.Label(cell, text=f"📌 시험", foreground="red", font=("Arial", 8)).pack()
                
                # 면학 계획 간략 표시
                if not is_weekend and date_str in self.data["plans"]:
                    plans = self.data["plans"][date_str]
                    markers = []
                    if plans.get("8면"): markers.append("8")
                    if plans.get("1면"): markers.append("1")
                    if plans.get("2면"): markers.append("2")
                    if markers:
                        ttk.Label(cell, text=" ".join(markers), foreground="green").pack()
                
                # 클릭 이벤트
                cell.bind("<Button-1>", lambda e, d=date_str: self.on_date_click(d))
                date_lbl.bind("<Button-1>", lambda e, d=date_str: self.on_date_click(d))
                
                col += 1
            week_num += 1
        
        # 그리드 가중치 설정
        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1)
        for i in range(week_num + 1):
            self.calendar_frame.grid_rowconfigure(i, weight=1)
    
    def render_year_view(self):
        """년 뷰 렌더링"""
        year = self.current_date.year
        
        # 12개월 그리드 (3x4)
        months_per_row = 4
        rows = 3
        
        for row in range(rows):
            for col in range(months_per_row):
                month_num = row * months_per_row + col + 1
                
                # 월 프레임
                month_frame = ttk.Frame(self.calendar_frame, relief=tk.RIDGE, borderwidth=1)
                month_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                
                # 월 제목
                ttk.Label(month_frame, text=f"{month_num}월", font=("Arial", 14, "bold")).pack()
                
                # 간단한 달력
                cal = monthcalendar(year, month_num)
                inner_frame = ttk.Frame(month_frame)
                inner_frame.pack()
                
                # 요일 헤더 (간략)
                days = ["월", "화", "수", "목", "금", "토", "일"]
                for d_idx, day in enumerate(days):
                    ttk.Label(inner_frame, text=day[0], font=("Arial", 6), width=2).grid(row=0, column=d_idx)
                
                # 날짜
                for w_idx, week in enumerate(cal):
                    for d_idx, day in enumerate(week):
                        if day > 0:
                            date = datetime(year, month_num, day)
                            date_str = date.strftime("%Y-%m-%d")
                            
                            bg = "white"
                            fg = "black"
                            
                            # 주말
                            if date.weekday() >= 5:
                                fg = "blue"
                            
                            # 공휴일
                            if date_str in self.kr_holidays:
                                fg = "red"
                            
                            # 면학 계획 있음
                            if date_str in self.data["plans"]:
                                plans = self.data["plans"][date_str]
                                if any(plans.values()):
                                    bg = "lightgreen"
                            
                            # 시험 있음
                            if date_str in self.data["events"]:
                                exams = [e for e in self.data["events"][date_str] if e["type"] == "exam"]
                                if exams:
                                    bg = "lightcoral"
                            
                            lbl = tk.Label(inner_frame, text=str(day), font=("Arial", 7), 
                                         bg=bg, fg=fg, width=2, relief=tk.FLAT)
                            lbl.grid(row=w_idx+1, column=d_idx, padx=1, pady=1)
                            
                            # 클릭 이벤트
                            lbl.bind("<Button-1>", lambda e, d=date_str: self.on_date_click(d))
                
                self.calendar_frame.grid_rowconfigure(row, weight=1)
                self.calendar_frame.grid_columnconfigure(col, weight=1)
    
    def on_date_click(self, date_str):
        """날짜 클릭 시 상세 정보 표시"""
        self.selected_date = date_str
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = ["월", "화", "수", "목", "금", "토", "일"][date_obj.weekday()]
        
        # 상세 정보 창
        detail_win = tk.Toplevel(self.root)
        detail_win.title(f"{date_str} ({day_name}요일) 상세 정보")
        detail_win.geometry("500x600")
        
        # 날짜 표시
        ttk.Label(detail_win, text=f"{date_str} ({day_name}요일)", 
                 font=("Arial", 16, "bold")).pack(pady=10)
        
        # 공휴일 정보
        if date_str in self.kr_holidays:
            ttk.Label(detail_win, text=f"🎉 공휴일: {self.kr_holidays.get(date_str)}", 
                     foreground="red").pack(pady=5)
        
        # 면학 계획 프레임
        plan_frame = ttk.LabelFrame(detail_win, text="면학 계획", padding=10)
        plan_frame.pack(fill=tk.X, padx=10, pady=5)
        
        if date_obj.weekday() < 5:  # 평일만
            plans = self.data["plans"].get(date_str, {})
            
            for myeong in ["8면", "1면", "2면"]:
                var = tk.BooleanVar(value=plans.get(myeong, False))
                chk = ttk.Checkbutton(plan_frame, text=myeong, variable=var,
                                     command=lambda m=myeong, v=var: self.toggle_plan(date_str, m, v.get()))
                chk.pack(anchor=tk.W)
        else:
            ttk.Label(plan_frame, text="주말에는 면학 시간이 없습니다.").pack()
        
        # 이벤트 프레임
        event_frame = ttk.LabelFrame(detail_win, text="이벤트 (공휴일/시험)", padding=10)
        event_frame.pack(fill=tk.X, padx=10, pady=5)
        
        if date_str in self.data["events"]:
            for i, event in enumerate(self.data["events"][date_str]):
                event_type = "시험" if event["type"] == "exam" else "공휴일"
                frame = ttk.Frame(event_frame)
                frame.pack(fill=tk.X, pady=2)
                ttk.Label(frame, text=f"[{event_type}] {event['text']}").pack(side=tk.LEFT)
                ttk.Button(frame, text="삭제", 
                          command=lambda idx=i: self.remove_event(date_str, idx, event_frame)).pack(side=tk.RIGHT)
        else:
            ttk.Label(event_frame, text="등록된 이벤트가 없습니다.").pack()
        
        # 할 일 프레임
        todo_frame = ttk.LabelFrame(detail_win, text="할 일 목록", padding=10)
        todo_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.render_todos(todo_frame, date_str)
        
        # 닫기 버튼
        ttk.Button(detail_win, text="닫기", command=detail_win.destroy).pack(pady=10)
    
    def render_todos(self, parent, date_str):
        """할 일 목록 렌더링"""
        for widget in parent.winfo_children():
            widget.destroy()
        
        todos = self.data["todos"].get(date_str, [])
        
        if not todos:
            ttk.Label(parent, text="등록된 할 일이 없습니다.").pack()
            return
        
        for i, todo in enumerate(todos):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=2)
            
            var = tk.BooleanVar(value=todo["done"])
            chk = ttk.Checkbutton(frame, text=todo["text"], variable=var,
                                 command=lambda t=todo, v=var: self.toggle_todo(date_str, t, v.get()))
            chk.pack(side=tk.LEFT)
            
            ttk.Button(frame, text="삭제", 
                      command=lambda idx=i: self.remove_todo(date_str, idx, parent)).pack(side=tk.RIGHT)
    
    def toggle_plan(self, date_str, myeong, value):
        """면학 계획 토글"""
        if date_str not in self.data["plans"]:
            self.data["plans"][date_str] = {}
        self.data["plans"][date_str][myeong] = value
        self.save_data()
        self.status_var.set(f"{date_str} {myeong} {'활성화' if value else '비활성화'}")
        self.refresh_calendar()
    
    def add_myeonhak_plan(self):
        """면학 계획 추가 다이얼로그"""
        if not hasattr(self, 'selected_date'):
            messagebox.showwarning("경고", "먼저 날짜를 선택해주세요.")
            return
        
        date_obj = datetime.strptime(self.selected_date, "%Y-%m-%d")
        if date_obj.weekday() >= 5:
            messagebox.showinfo("알림", "주말에는 면학 시간이 없습니다.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("면학 계획 추가")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text=f"{self.selected_date} 면학 계획", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        for myeong in ["8면", "1면", "2면"]:
            var = tk.BooleanVar(value=self.data["plans"].get(self.selected_date, {}).get(myeong, False))
            chk = ttk.Checkbutton(dialog, text=myeong, variable=var)
            chk.pack(anchor=tk.W, padx=20)
            setattr(dialog, f"var_{myeong}", var)
        
        def save():
            plans = {}
            for myeong in ["8면", "1면", "2면"]:
                var = getattr(dialog, f"var_{myeong}")
                plans[myeong] = var.get()
            
            self.data["plans"][self.selected_date] = plans
            self.save_data()
            self.refresh_calendar()
            self.status_var.set("면학 계획이 저장되었습니다.")
            dialog.destroy()
        
        ttk.Button(dialog, text="저장", command=save).pack(pady=10)
    
    def add_todo(self):
        """할 일 추가"""
        if not hasattr(self, 'selected_date'):
            messagebox.showwarning("경고", "먼저 날짜를 선택해주세요.")
            return
        
        todo = simpledialog.askstring("할 일 추가", "할 일을 입력하세요:")
        if todo:
            if self.selected_date not in self.data["todos"]:
                self.data["todos"][self.selected_date] = []
            self.data["todos"][self.selected_date].append({"text": todo, "done": False})
            self.save_data()
            self.status_var.set("할 일이 추가되었습니다.")
            self.refresh_calendar()
    
    def toggle_todo(self, date_str, todo, done):
        """할 일 완료 토글"""
        todos = self.data["todos"].get(date_str, [])
        for t in todos:
            if t["text"] == todo["text"]:
                t["done"] = done
                break
        self.save_data()
        self.status_var.set(f"할 일 {'완료' if done else '미완료'} 처리됨")
    
    def remove_todo(self, date_str, index, parent):
        """할 일 삭제"""
        if date_str in self.data["todos"]:
            del self.data["todos"][date_str][index]
            if not self.data["todos"][date_str]:
                del self.data["todos"][date_str]
            self.save_data()
            self.render_todos(parent, date_str)
            self.refresh_calendar()
            self.status_var.set("할 일이 삭제되었습니다.")
    
    def add_event(self):
        """이벤트 추가"""
        if not hasattr(self, 'selected_date'):
            messagebox.showwarning("경고", "먼저 날짜를 선택해주세요.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("이벤트 추가")
        dialog.geometry("350x200")
        
        ttk.Label(dialog, text=f"{self.selected_date} 이벤트 추가", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        ttk.Label(dialog, text="이벤트 유형:").pack(anchor=tk.W, padx=20)
        event_type = ttk.Combobox(dialog, values=["시험", "기타"], state="readonly")
        event_type.set("시험")
        event_type.pack(anchor=tk.W, padx=20, pady=5)
        
        ttk.Label(dialog, text="이벤트 내용:").pack(anchor=tk.W, padx=20)
        event_text = ttk.Entry(dialog, width=40)
        event_text.pack(anchor=tk.W, padx=20, pady=5)
        
        def save():
            text = event_text.get().strip()
            if not text:
                messagebox.showwarning("경고", "이벤트 내용을 입력하세요.")
                return
            
            if self.selected_date not in self.data["events"]:
                self.data["events"][self.selected_date] = []
            
            event_type_map = {"시험": "exam", "기타": "other"}
            self.data["events"][self.selected_date].append({
                "type": event_type_map[event_type.get()],
                "text": text
            })
            self.save_data()
            self.refresh_calendar()
            self.status_var.set("이벤트가 추가되었습니다.")
            dialog.destroy()
        
        ttk.Button(dialog, text="저장", command=save).pack(pady=10)
    
    def remove_event(self, date_str, index, parent):
        """이벤트 삭제"""
        if date_str in self.data["events"]:
            del self.data["events"][date_str][index]
            if not self.data["events"][date_str]:
                del self.data["events"][date_str]
            self.save_data()
            # 부모 창 새로고침
            for widget in parent.winfo_children():
                widget.destroy()
            if date_str in self.data["events"]:
                for i, event in enumerate(self.data["events"][date_str]):
                    event_type = "시험" if event["type"] == "exam" else "공휴일"
                    frame = ttk.Frame(parent)
                    frame.pack(fill=tk.X, pady=2)
                    ttk.Label(frame, text=f"[{event_type}] {event['text']}").pack(side=tk.LEFT)
                    ttk.Button(frame, text="삭제", 
                              command=lambda idx=i: self.remove_event(date_str, idx, parent)).pack(side=tk.RIGHT)
            else:
                ttk.Label(parent, text="등록된 이벤트가 없습니다.").pack()
            self.refresh_calendar()
            self.status_var.set("이벤트가 삭제되었습니다.")
    
    def delete_selected(self):
        """선택된 날짜의 모든 데이터 삭제"""
        if not hasattr(self, 'selected_date'):
            messagebox.showwarning("경고", "먼저 날짜를 선택해주세요.")
            return
        
        if messagebox.askyesno("확인", f"{self.selected_date}의 모든 계획을 삭제하시겠습니까?"):
            self.data["plans"].pop(self.selected_date, None)
            self.data["todos"].pop(self.selected_date, None)
            self.data["events"].pop(self.selected_date, None)
            self.save_data()
            self.refresh_calendar()
            self.status_var.set("모든 데이터가 삭제되었습니다.")
    
    def show_stats(self):
        """통계 표시"""
        total_plans = sum(len(p) for p in self.data["plans"].values())
        total_todos = sum(len(t) for t in self.data["todos"].values())
        completed_todos = sum(1 for todos in self.data["todos"].values() for t in todos if t["done"])
        total_events = sum(len(e) for e in self.data["events"].values())
        
        # 면학 종류별 통계
        myeong_stats = {"8면": 0, "1면": 0, "2면": 0}
        for plans in self.data["plans"].values():
            for myeong, active in plans.items():
                if active:
                    myeong_stats[myeong] += 1
        
        stats_win = tk.Toplevel(self.root)
        stats_win.title("통계")
        stats_win.geometry("400x400")
        
        ttk.Label(stats_win, text="📊 면학 관리 통계", font=("Arial", 16, "bold")).pack(pady=10)
        
        info = f"""
        총 면학 계획일: {total_plans}회
        - 8면: {myeong_stats['8면']}회
        - 1면: {myeong_stats['1면']}회
        - 2면: {myeong_stats['2면']}회
        
        총 할 일: {total_todos}개
        완료된 할 일: {completed_todos}개
        미완료 할 일: {total_todos - completed_todos}개
        
        총 이벤트: {total_events}개
        """
        
        ttk.Label(stats_win, text=info, justify=tk.LEFT, font=("Arial", 12)).pack(pady=20)
        
        ttk.Button(stats_win, text="닫기", command=stats_win.destroy).pack()
    
    def set_view(self, view):
        """뷰 변경"""
        self.current_view = view
        self.refresh_calendar()
    
    def prev_period(self):
        """이전 기간으로 이동"""
        if self.current_view == "week":
            self.current_date -= timedelta(days=7)
        elif self.current_view == "month":
            if self.current_date.month == 1:
                self.current_date = datetime(self.current_date.year - 1, 12, 1)
            else:
                self.current_date = datetime(self.current_date.year, self.current_date.month - 1, 1)
        else:  # year
            self.current_date = datetime(self.current_date.year - 1, 1, 1)
        self.refresh_calendar()
    
    def next_period(self):
        """다음 기간으로 이동"""
        if self.current_view == "week":
            self.current_date += timedelta(days=7)
        elif self.current_view == "month":
            if self.current_date.month == 12:
                self.current_date = datetime(self.current_date.year + 1, 1, 1)
            else:
                self.current_date = datetime(self.current_date.year, self.current_date.month + 1, 1)
        else:  # year
            self.current_date = datetime(self.current_date.year + 1, 1, 1)
        self.refresh_calendar()
    
    def go_to_today(self):
        """오늘로 이동"""
        self.current_date = datetime.now()
        self.refresh_calendar()


if __name__ == "__main__":
    root = tk.Tk()
    app = MyeonhakManager(root)
    root.mainloop()
