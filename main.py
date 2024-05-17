from PyQt5.QtCore import QSize, QThread, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout
from bs4 import BeautifulSoup
import requests
import sys
import time


            
# 아이피 업데이트를 실행할 쓰레드
class proccessThread(QThread):
    def __init__(self, path):
        super().__init__()
        self.current_ip = "0.0.0.0"
        self.current_state_info = "Idle"
        self.save_path = path

    def run(self):
        while True:
            # 내 아이피 가져오기
            url = 'https://ip.pe.kr/'
            response = requests.get(url)
            # 요청이 성공했는지 확인
            if response.status_code == 200:
                state_info = "Request Succeed"
            else:
                state_info = "Request Failed"
            soup = BeautifulSoup(response.content, 'html.parser')
            new_ip = soup.select_one(".cover-heading").get_text() # 내 아이피
            # 상태 변경 감지
            if (self.current_ip != new_ip) or (self.current_state_info != state_info):
                # 값 업데이트
                self.current_ip = new_ip
                self.current_state_info = state_info
                # 아이피 변경시 파일을 변경
                with open(f'{self.save_path}\ip_log.txt', 'a') as file:
                    # 아이피 로그
                    tm = time.localtime(time.time())
                    file.write(f"[{tm.tm_year}-{tm.tm_mon}-{tm.tm_mday}-{tm.tm_hour}:{tm.tm_min}] {self.current_state_info:>15}) 외부 아이피: {new_ip}\n")
                        
            # 추적 간격 (너무 빠르면 오류 발생 가능) 5분 간격
            time.sleep(60 * 5)



# 위젯 생성
class IP_Update(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.save_path = ""

    def initUI(self):
        self.stateLable = QLabel(f"상태: 대기")
        font = self.stateLable.font()
        font.setPointSize(10)
        self.stateLable.setAlignment(Qt.AlignCenter)
        self.stateLable.setFont(font)

        self.selfolderLabel = QLabel(f"폴더를 선택하세요")
        font = self.selfolderLabel.font()
        font.setPointSize(10)
        self.selfolderLabel.setAlignment(Qt.AlignCenter)
        self.selfolderLabel.setFont(font)

        self.selBtn = QPushButton('폴더 열기')
        font = self.selBtn.font()
        font.setPointSize(10)
        self.selBtn.setFont(font)
        self.selBtn.clicked.connect(self.SelBtnClicked)

        self.startBtn = QPushButton('Start')
        font = self.startBtn.font()
        font.setPointSize(10)
        self.startBtn.setFont(font)
        self.startBtn.clicked.connect(self.StartBtnClicked)
        
        # 파일 선택
        hbox_2 = QHBoxLayout()
        hbox_2.addStretch(1)
        hbox_2.addWidget(self.selfolderLabel)
        hbox_2.addWidget(self.selBtn)
        hbox_2.addStretch(1)

        # 상태 표시
        hbox_1 = QHBoxLayout()
        hbox_1.addStretch(1)
        hbox_1.addWidget(self.stateLable)
        hbox_1.addWidget(self.startBtn)
        hbox_1.addStretch(1)

        # 위아래
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox_1)
        vbox.addLayout(hbox_2)
        vbox.addStretch(1)

        self.setLayout(vbox)

        self.setWindowTitle('IP_Update')
        self.move(300, 300)
        self.setFixedSize(QSize(500, 100))
        self.show()

    def SelBtnClicked(self):
        fname = QFileDialog.getExistingDirectory(self, '파일 선택')
        self.save_path = fname
        self.selfolderLabel.setText(f"위치: {fname}/ip_log.txt") # 파일 경로
        
    # 기록 시작
    def StartBtnClicked(self):
        if self.save_path != "":
            self.stateLable.setText("상태: 기록 중... (5분 간격)")
            self.startBtn.setEnabled(False)
            self.selBtn.setEnabled(False)
            self.process = proccessThread(self.save_path)
            self.process.start()
        else:
            self.selfolderLabel.setText("폴더 잘못 됨")


if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = IP_Update()
   sys.exit(app.exec_())