import sys
import psutil
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QLineEdit, QPushButton, 
                             QListWidget, QMessageBox, QGroupBox)

class MyCheatTool(QWidget):
    def __init__(self):
        super().__init__()
        self.all_procs = [] # 모든 프로세스 목록을 임시 저장할 변수
        self.initUI()
        self.refresh_process_list() 

    def initUI(self):
        self.setWindowTitle('나만의 치트 툴 v1.2 (검색 기능 추가)')
        self.setGeometry(300, 300, 400, 550) # 검색창 때문에 높이를 조금 늘림

        main_layout = QVBoxLayout()

        # --- 구역 1: 프로세스 선택 (업그레이드 됨) ---
        process_group = QGroupBox("1. 타겟 프로세스 선택")
        process_layout = QVBoxLayout() # 검색창과 콤보박스를 위아래로 배치

        # [1] 검색창 추가
        self.input_proc_search = QLineEdit()
        self.input_proc_search.setPlaceholderText("여기에 프로세스 이름 검색 (예: note, game)")
        self.input_proc_search.textChanged.connect(self.filter_process_list) # 글자 칠 때마다 필터링 함수 실행

        # [2] 프로세스 목록 박스 + 새로고침 버튼
        combo_layout = QHBoxLayout()
        self.process_combo = QComboBox()
        btn_refresh = QPushButton("새로고침")
        btn_refresh.clicked.connect(self.refresh_process_list)

        combo_layout.addWidget(self.process_combo)
        combo_layout.addWidget(btn_refresh)

        process_layout.addWidget(self.input_proc_search) # 검색창 배치
        process_layout.addLayout(combo_layout)           # 목록 박스 배치
        process_group.setLayout(process_layout)

        # --- 구역 2: 스캔 제어 ---
        scan_group = QGroupBox("2. 값 검색 (Scanner)")
        scan_layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("찾을 값:"))
        self.input_value = QLineEdit()
        self.input_value.setPlaceholderText("예: 100")
        input_layout.addWidget(self.input_value)
        btn_layout = QHBoxLayout()
        self.btn_first_scan = QPushButton("First Scan")
        self.btn_next_scan = QPushButton("Next Scan")
        self.btn_first_scan.clicked.connect(self.first_scan)
        self.btn_next_scan.clicked.connect(self.next_scan)
        btn_layout.addWidget(self.btn_first_scan)
        btn_layout.addWidget(self.btn_next_scan)
        scan_layout.addLayout(input_layout)
        scan_layout.addLayout(btn_layout)
        scan_group.setLayout(scan_layout)

        # --- 구역 3: 결과 목록 ---
        result_group = QGroupBox("3. 검색 결과")
        result_layout = QVBoxLayout()
        self.result_list = QListWidget()
        result_layout.addWidget(self.result_list)
        result_group.setLayout(result_layout)

        # --- 구역 4: 값 수정 ---
        edit_group = QGroupBox("4. 값 변경")
        edit_layout = QHBoxLayout()
        self.input_new_value = QLineEdit()
        self.input_new_value.setPlaceholderText("변경할 값")
        btn_write = QPushButton("값 적용!")
        btn_write.setStyleSheet("background-color: #ffcccc; font-weight: bold;")
        btn_write.clicked.connect(self.write_value)
        edit_layout.addWidget(self.input_new_value)
        edit_layout.addWidget(btn_write)
        edit_group.setLayout(edit_layout)

        main_layout.addWidget(process_group)
        main_layout.addWidget(scan_group)
        main_layout.addWidget(result_group)
        main_layout.addWidget(edit_group)
        self.setLayout(main_layout)

    # --- 기능 함수들 ---
    def refresh_process_list(self):
        """모든 프로세스를 불러와서 저장만 해두고, 필터링 함수를 호출합니다."""
        self.all_procs = [] # 초기화
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    name = proc.info['name']
                    pid = proc.info['pid']
                    display_text = f"[{pid}] {name}"
                    self.all_procs.append(display_text)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            print(f"프로세스 읽기 에러: {e}")

        self.all_procs.sort()
        # 목록을 다 가져왔으니 필터링을 한번 돌려줍니다 (검색창이 비어있으면 다 뜸)
        self.filter_process_list()
        print("프로세스 목록 갱신 완료!")

    def filter_process_list(self):
        """검색창에 입력된 글자에 따라 콤보박스 내용을 바꿉니다."""
        search_text = self.input_proc_search.text().lower() # 소문자로 변환 (대소문자 무시)
        
        self.process_combo.clear() # 콤보박스 비우기
        
        filtered_items = []
        for item in self.all_procs:
            # 검색어가 아이템 이름에 포함되어 있으면 추가
            if search_text in item.lower():
                filtered_items.append(item)
        
        if not filtered_items:
            self.process_combo.addItem("검색 결과 없음")
        else:
            self.process_combo.addItems(filtered_items)

    def first_scan(self):
        val = self.input_value.text()
        print(f"First Scan: {val}")
        self.result_list.clear()
        self.result_list.addItems(["Scanning...", "구현 예정"])

    def next_scan(self):
        print("Next Scan")

    def write_value(self):
        new_val = self.input_new_value.text()
        QMessageBox.information(self, "알림", f"{new_val} (구현 예정)")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyCheatTool()
    ex.show()
    sys.exit(app.exec_())