#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
면학 불참 계획 기록 프로그램

학교의 8면, 1면, 2면 면학 시간에 대한 불참 계획표 관리 및
날짜별 할 일 목록 정리를 할 수 있는 프로그램입니다.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

DATA_FILE = "myeonhak_data.json"


class MyeonhakManager:
    """면학 불참 및 할 일 관리 클래스"""
    
    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = data_file
        self.data = self.load_data()
    
    def load_data(self) -> Dict:
        """데이터 파일에서 데이터 로드"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # 기본 데이터 구조
        return {
            "exemptions": [],  # 면학 불참 기록
            "todos": {}  # 날짜별 할 일 목록 (key: 날짜 문자열)
        }
    
    def save_data(self):
        """데이터를 파일에 저장"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_exemption(self, date: str, myeon_type: str, reason: str, status: str = "계획") -> bool:
        """
        면학 불참 기록 추가
        
        Args:
            date: 날짜 (YYYY-MM-DD 형식 권장)
            myeon_type: 면학 종류 (8면, 1면, 2면)
            reason: 불참 사유
            status: 상태 (계획, 완료, 취소)
        """
        valid_types = ["8면", "1면", "2면"]
        if myeon_type not in valid_types:
            print(f"❌ 오류: 면학 종류는 {', '.join(valid_types)} 중 하나여야 합니다.")
            return False
        
        exemption = {
            "id": len(self.data["exemptions"]) + 1,
            "date": date,
            "myeon_type": myeon_type,
            "reason": reason,
            "status": status,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.data["exemptions"].append(exemption)
        self.save_data()
        print(f"✅ 면학 불참이 등록되었습니다: {date} - {myeon_type} ({reason})")
        return True
    
    def list_exemptions(self, filter_date: Optional[str] = None, 
                       filter_type: Optional[str] = None,
                       filter_status: Optional[str] = None):
        """면학 불참 목록 조회"""
        exemptions = self.data["exemptions"]
        
        if filter_date:
            exemptions = [e for e in exemptions if filter_date in e["date"]]
        if filter_type:
            exemptions = [e for e in exemptions if e["myeon_type"] == filter_type]
        if filter_status:
            exemptions = [e for e in exemptions if e["status"] == filter_status]
        
        if not exemptions:
            print("📭 등록된 면학 불참 기록이 없습니다.")
            return
        
        print("\n" + "=" * 70)
        print("📋 면학 불참 목록")
        print("=" * 70)
        print(f"{'ID':<5} {'날짜':<12} {'면학':<6} {'상태':<8} {'사유':<30}")
        print("-" * 70)
        
        for e in exemptions:
            print(f"{e['id']:<5} {e['date']:<12} {e['myeon_type']:<6} {e['status']:<8} {e['reason']:<30}")
        
        print("=" * 70)
        print(f"총 {len(exemptions)}개 기록")
    
    def update_exemption_status(self, exemption_id: int, new_status: str) -> bool:
        """면학 불참 상태 업데이트"""
        valid_statuses = ["계획", "완료", "취소"]
        if new_status not in valid_statuses:
            print(f"❌ 오류: 상태는 {', '.join(valid_statuses)} 중 하나여야 합니다.")
            return False
        
        for exemption in self.data["exemptions"]:
            if exemption["id"] == exemption_id:
                exemption["status"] = new_status
                self.save_data()
                print(f"✅ 상태가 업데이트되었습니다: {exemption['myeon_type']} - {new_status}")
                return True
        
        print(f"❌ 오류: ID {exemption_id}에 해당하는 기록을 찾을 수 없습니다.")
        return False
    
    def delete_exemption(self, exemption_id: int) -> bool:
        """면학 불참 기록 삭제"""
        for i, exemption in enumerate(self.data["exemptions"]):
            if exemption["id"] == exemption_id:
                deleted = self.data["exemptions"].pop(i)
                self.save_data()
                print(f"✅ 기록이 삭제되었습니다: {deleted['date']} - {deleted['myeon_type']}")
                return True
        
        print(f"❌ 오류: ID {exemption_id}에 해당하는 기록을 찾을 수 없습니다.")
        return False
    
    def add_todo(self, date: str, task: str) -> bool:
        """
        날짜별 할 일 추가
        
        Args:
            date: 날짜 (YYYY-MM-DD 형식 권장)
            task: 할 일 내용
        """
        if date not in self.data["todos"]:
            self.data["todos"][date] = []
        
        todo_item = {
            "id": len(self.data["todos"][date]) + 1,
            "task": task,
            "completed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.data["todos"][date].append(todo_item)
        self.save_data()
        print(f"✅ 할 일이 추가되었습니다: {date} - {task}")
        return True
    
    def list_todos(self, date: Optional[str] = None):
        """할 일 목록 조회"""
        if date:
            dates_to_show = {date: self.data["todos"].get(date, [])}
        else:
            dates_to_show = self.data["todos"]
        
        if not dates_to_show or all(len(v) == 0 for v in dates_to_show.values()):
            print("📭 등록된 할 일이 없습니다.")
            return
        
        print("\n" + "=" * 70)
        print("📝 날짜별 할 일 목록")
        print("=" * 70)
        
        for current_date in sorted(dates_to_show.keys()):
            todos = dates_to_show[current_date]
            if not todos:
                continue
            
            print(f"\n📅 {current_date}")
            print("-" * 70)
            
            for todo in todos:
                status = "✓" if todo["completed"] else "○"
                print(f"  [{status}] {todo['task']}")
        
        print("\n" + "=" * 70)
    
    def complete_todo(self, date: str, todo_id: int) -> bool:
        """할 일 완료 처리"""
        if date not in self.data["todos"]:
            print(f"❌ 오류: {date} 날짜의 할 일 목록이 없습니다.")
            return False
        
        for todo in self.data["todos"][date]:
            if todo["id"] == todo_id:
                todo["completed"] = True
                self.save_data()
                print(f"✅ 할 일이 완료 처리되었습니다: {todo['task']}")
                return True
        
        print(f"❌ 오류: ID {todo_id}에 해당하는 할 일을 찾을 수 없습니다.")
        return False
    
    def delete_todo(self, date: str, todo_id: int) -> bool:
        """할 일 삭제"""
        if date not in self.data["todos"]:
            print(f"❌ 오류: {date} 날짜의 할 일 목록이 없습니다.")
            return False
        
        for i, todo in enumerate(self.data["todos"][date]):
            if todo["id"] == todo_id:
                deleted = self.data["todos"][date].pop(i)
                self.save_data()
                print(f"✅ 할 일이 삭제되었습니다: {deleted['task']}")
                return True
        
        print(f"❌ 오류: ID {todo_id}에 해당하는 할 일을 찾을 수 없습니다.")
        return False
    
    def get_statistics(self):
        """통계 정보 표시"""
        print("\n" + "=" * 70)
        print("📊 면학 불참 통계")
        print("=" * 70)
        
        total = len(self.data["exemptions"])
        if total == 0:
            print("등록된 기록이 없습니다.")
            return
        
        by_type = {}
        by_status = {}
        
        for e in self.data["exemptions"]:
            # 면학 종류별
            myeon_type = e["myeon_type"]
            by_type[myeon_type] = by_type.get(myeon_type, 0) + 1
            
            # 상태별
            status = e["status"]
            by_status[status] = by_status.get(status, 0) + 1
        
        print(f"\n총 기록 수: {total}개")
        
        print("\n면학 종류별:")
        for myeon_type in ["8면", "1면", "2면"]:
            count = by_type.get(myeon_type, 0)
            print(f"  {myeon_type}: {count}개")
        
        print("\n상태별:")
        for status in ["계획", "완료", "취소"]:
            count = by_status.get(status, 0)
            print(f"  {status}: {count}개")
        
        print("=" * 70)


def print_menu():
    """메뉴 표시"""
    print("\n" + "=" * 70)
    print("🎓 면학 불참 계획 기록 프로그램")
    print("=" * 70)
    print("1. 면학 불참 등록")
    print("2. 면학 불참 목록 조회")
    print("3. 면학 불참 상태 변경")
    print("4. 면학 불참 삭제")
    print("5. 할 일 추가")
    print("6. 할 일 목록 조회")
    print("7. 할 일 완료 처리")
    print("8. 할 일 삭제")
    print("9. 통계 보기")
    print("0. 종료")
    print("=" * 70)


def main():
    """메인 함수"""
    manager = MyeonhakManager()
    
    while True:
        print_menu()
        
        try:
            choice = input("선택하세요 (0-9): ").strip()
            
            if choice == "0":
                print("\n👋 프로그램을 종료합니다.")
                break
            
            elif choice == "1":  # 면학 불참 등록
                print("\n--- 면학 불참 등록 ---")
                date = input("날짜 (YYYY-MM-DD): ").strip()
                print("면학 종류: 1) 8면  2) 1면  3) 2면")
                type_choice = input("선택 (1-3): ").strip()
                
                myeon_map = {"1": "8면", "2": "1면", "3": "2면"}
                myeon_type = myeon_map.get(type_choice, "")
                
                if not myeon_type:
                    print("❌ 잘못된 선택입니다.")
                    continue
                
                reason = input("불참 사유: ").strip()
                manager.add_exemption(date, myeon_type, reason)
            
            elif choice == "2":  # 면학 불참 목록 조회
                print("\n--- 면학 불참 목록 조회 ---")
                print("필터 옵션 (엔터시면 전체 조회):")
                filter_date = input("  날짜 필터 (YYYY-MM-DD 또는 엔터): ").strip() or None
                print("  면학 종류: 1) 8면  2) 1면  3) 2면  4) 전체")
                type_choice = input("  선택 (1-4 또는 엔터): ").strip()
                
                filter_type = None
                if type_choice in ["1", "2", "3"]:
                    myeon_map = {"1": "8면", "2": "1면", "3": "2면"}
                    filter_type = myeon_map[type_choice]
                
                print("  상태: 1) 계획  2) 완료  3) 취소  4) 전체")
                status_choice = input("  선택 (1-4 또는 엔터): ").strip()
                
                filter_status = None
                if status_choice in ["1", "2", "3"]:
                    status_map = {"1": "계획", "2": "완료", "3": "취소"}
                    filter_status = status_map[status_choice]
                
                manager.list_exemptions(filter_date, filter_type, filter_status)
            
            elif choice == "3":  # 면학 불참 상태 변경
                print("\n--- 면학 불참 상태 변경 ---")
                try:
                    exemption_id = int(input("변경할 기록 ID: ").strip())
                    print("새 상태: 1) 계획  2) 완료  3) 취소")
                    status_choice = input("선택 (1-3): ").strip()
                    
                    status_map = {"1": "계획", "2": "완료", "3": "취소"}
                    new_status = status_map.get(status_choice, "")
                    
                    if new_status:
                        manager.update_exemption_status(exemption_id, new_status)
                    else:
                        print("❌ 잘못된 선택입니다.")
                except ValueError:
                    print("❌ 숫자를 입력해주세요.")
            
            elif choice == "4":  # 면학 불참 삭제
                print("\n--- 면학 불참 삭제 ---")
                try:
                    exemption_id = int(input("삭제할 기록 ID: ").strip())
                    confirm = input(f"정말로 ID {exemption_id} 기록을 삭제하시겠습니까? (y/n): ").strip().lower()
                    if confirm == 'y':
                        manager.delete_exemption(exemption_id)
                except ValueError:
                    print("❌ 숫자를 입력해주세요.")
            
            elif choice == "5":  # 할 일 추가
                print("\n--- 할 일 추가 ---")
                date = input("날짜 (YYYY-MM-DD): ").strip()
                task = input("할 일 내용: ").strip()
                if date and task:
                    manager.add_todo(date, task)
                else:
                    print("❌ 날짜와 할 일 내용을 모두 입력해주세요.")
            
            elif choice == "6":  # 할 일 목록 조회
                print("\n--- 할 일 목록 조회 ---")
                date = input("조회할 날짜 (YYYY-MM-DD 또는 엔터로 전체): ").strip() or None
                manager.list_todos(date)
            
            elif choice == "7":  # 할 일 완료 처리
                print("\n--- 할 일 완료 처리 ---")
                date = input("날짜 (YYYY-MM-DD): ").strip()
                try:
                    todo_id = int(input("완료할 할 일 ID: ").strip())
                    manager.complete_todo(date, todo_id)
                except ValueError:
                    print("❌ 숫자를 입력해주세요.")
            
            elif choice == "8":  # 할 일 삭제
                print("\n--- 할 일 삭제 ---")
                date = input("날짜 (YYYY-MM-DD): ").strip()
                try:
                    todo_id = int(input("삭제할 할 일 ID: ").strip())
                    confirm = input(f"정말로 삭제하시겠습니까? (y/n): ").strip().lower()
                    if confirm == 'y':
                        manager.delete_todo(date, todo_id)
                except ValueError:
                    print("❌ 숫자를 입력해주세요.")
            
            elif choice == "9":  # 통계 보기
                manager.get_statistics()
            
            else:
                print("❌ 잘못된 선택입니다. 0-9 사이의 숫자를 입력해주세요.")
        
        except KeyboardInterrupt:
            print("\n\n👋 프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()
