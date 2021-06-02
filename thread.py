import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QProgressBar, QPushButton)
from PyQt5.QtCore import QThread, pyqtSignal
import time

class Thread(QThread):
    update_signal = pyqtSignal(int) 

    def __init__(self, *args, **kwargs):
        super(Thread, self).__init__(*args, **kwargs)
        self.count   = 0
        self.running = True

    def run(self):
        # while self.running and self.count < 100:
        self.count = self.index
        print("count", self.count)
        self.update_signal.emit(self.count)
        # QThread.msleep(100)                   

class Thread2(QThread):
    update_signal2 = pyqtSignal(int) 

    def __init__(self, *args, **kwargs):
        super(Thread2, self).__init__(*args, **kwargs)
        self.count   = 0
        self.running = True

    def run(self):
        # while self.running and self.count < 100:
        self.count = self.index
        print("count", self.count)
        self.update_signal2.emit(self.count)
        # QThread.msleep(100)     

class Actions(QDialog):
    """
        Simple dialog that consists of a Progress Bar and a Button.
        Clicking on the button results in the start of a timer and
        updates the progress bar.
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Progress Bar')
        self.progress = QProgressBar(self)
        self.progress.setGeometry(0, 0, 300, 100)
        self.progress.setMaximum(100)
        self.progress.setValue(0)

        self.progress2 = QProgressBar(self)
        self.progress2.setGeometry(0, 120, 300, 100)
        self.progress2.setMaximum(100)
        self.progress2.setValue(0)

        self.button = QPushButton('Start1', self)
        self.button.move(0, 330)
        # self.button2 = QPushButton('Start2', self)
        # self.button2.setEnabled(True)
        # self.button2.move(00, 390)

        self.button.clicked.connect(self.onButtonClick)
        # self.button2.clicked.connect(self.onButtonClick2)

        self.thread = Thread()
        self.thread.update_signal.connect(self.update)

        self.thread2 = Thread2()
        self.thread2.update_signal2.connect(self.update)

    def onButtonClick(self):
        def get_data():
            def get_ids():
                self.datas = ['apple', 'cat', 'dog'] *10
                self.datas = [f'ap{i}' for i in range(100000)]
            get_ids()
            for data in self.datas:
                
                self.thread.index = int((self.datas.index(data) *100) / len(self.datas))
                # time.sleep(2)
                print(self.thread.index)
        # self.button2.setEnabled(True)
        # self.progress.setValue(0)
        # self.thread.running = True
        # self.thread.count = 0
                self.thread.start()
                # self.button.setEnabled(False)
        get_data()
        self.thread2.index = 100
        self.thread2.start()

    def update(self, val):
        self.progress.setValue(val)
        # if val == 100: self.on_stop()

    # def on_stop(self):
    #     self.thread.stop()
    #     self.button.setEnabled(True)
    #     self.button2.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Actions()
    window.show()
    sys.exit(app.exec_())









# from PyQt5 import QtGui
# from PyQt5.QtWidgets import QApplication, QDialog, QProgressBar, QPushButton, QVBoxLayout
# import sys
# from PyQt5.QtCore import Qt, QThread, pyqtSignal
# import time


# class MyThread(QThread):
#     # Create a counter thread
#     change_value = pyqtSignal(int)
#     def __init__(self, val):
#         self.val = val
#     def run(self):
#         cnt = 0
#         while cnt < self.val:
#             cnt+=1
#             time.sleep(0.3)
#             self.change_value.emit(cnt)
# class Window(QDialog):
#     def __init__(self):
#         super().__init__()
#         self.title = "PyQt5 ProgressBar"
#         self.top = 200
#         self.left = 500
#         self.width = 300
#         self.height = 100
#         self.setWindowIcon(QtGui.QIcon("icon.png"))
#         self.setWindowTitle(self.title)
#         self.setGeometry(self.left, self.top, self.width, self.height)
#         vbox = QVBoxLayout()
#         self.progressbar = QProgressBar()
#         #self.progressbar.setOrientation(Qt.Vertical)
#         self.progressbar.setMaximum(100)
#         self.progressbar.setStyleSheet("QProgressBar {border: 2px solid grey;border-radius:8px;padding:1px}"
#                                        "QProgressBar::chunk {background:yellow}")
#         #qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 red, stop: 1 white);
#         #self.progressbar.setStyleSheet("QProgressBar::chunk {background: qlineargradient(x1: 0, y1: 0.5, x2: 1, y2: 0.5, stop: 0 red, stop: 1 white); }")
#         #self.progressbar.setTextVisible(False)
#         vbox.addWidget(self.progressbar)
#         self.button = QPushButton("Start Progressbar")
#         self.button.clicked.connect(self.startProgressBar)
#         self.button.setStyleSheet('background-color:yellow')
#         vbox.addWidget(self.button)
#         self.setLayout(vbox)
#         self.show()

#     def startProgressBar(self):
#         self.thread = MyThread(25)
#         self.thread.change_value.connect(self.setProgressVal)
#         self.thread.start()

#     def setProgressVal(self, val):
#         self.progressbar.setValue(val)



# App = QApplication(sys.argv)
# window = Window()
# sys.exit(App.exec())