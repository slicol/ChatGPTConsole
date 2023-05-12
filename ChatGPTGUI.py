import time
from PyQt5.QtWidgets import (
    QPushButton,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSplitter, 
    QSlider
)
import threading
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMenu, QAction, QSystemTrayIcon
from ChatGPTConsole import ChatAPI, ChatBot, ChatContext
import os
from datetime import datetime
import Misc.MTFileUtils as MTFileUtils
from Misc.MTConfigIni import GMTConfig
import openai



class CodeGroup(object):
    def __init__(self) -> None:
        pass
    def __enter__(self):
        pass
    def __exit__(self, *args):
        pass


class NameDialog(QtWidgets.QDialog):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("请输入你的名字")
        self.setFixedSize(500, 100)
        layout = QtWidgets.QVBoxLayout()

        self.name_input = QtWidgets.QLineEdit()
        
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | 
            QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(self.name_input)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def accept(self):
        username = self.name_input.text()
        username = username.strip()
        if username == '':
            self.setWindowTitle("请输入你的名字[不能为空]")
        else:
            ChatContext.username = username
            super().accept()
        pass


def ChatDebugEcho(usermsg):return usermsg


class FileExplorLabel(QLabel):
    explor_path = ''
    def mouseDoubleClickEvent(self, event):
        if os.path.exists(self.explor_path):
            os.startfile(self.explor_path)
        pass
        event.accept()
        return

    def SetExplorPath(self, path:str):
        self.explor_path = path
        return
    

class ChatWindow(QtWidgets.QWidget):
    timeoutCoundown = 0
    timeoutTimer = None

    def __init__(self):
        super().__init__()

        self.timeoutCoundown = 0
        self.timeoutTimer = QTimer()

        self.setWindowTitle("ChatGPTGUI [ Welcome, {} ]".format(ChatContext.username))
        self.resize(1024, 800)

        vbox = QVBoxLayout()
        
        # 创建一个 QSplitter 控件
        splitter = QSplitter(Qt.Vertical, self)
        vbox.addWidget(splitter)
        splitter.setStyleSheet("QSplitter::handle { background-color: #505050; }")
        
        with CodeGroup():
            vbox_chat_box = QVBoxLayout()
            
            frame = QtWidgets.QWidget()
            frame.setLayout(vbox_chat_box)
            
            curdir = os.getcwd()
            curdir = curdir.replace('\\','/')
            session_dir = curdir + '/log/'
            label = FileExplorLabel("Message List:" + f"({session_dir})")
            label.SetExplorPath(session_dir)
            vbox_chat_box.addWidget(label)

            self.chat_box = QTextEdit()
            self.chat_box.setReadOnly(True)
            vbox_chat_box.addWidget(self.chat_box)

            #frame.setStyleSheet("QWidget {padding: 0px;margin-left: 0px;spacing:0px;}")
            splitter.addWidget(frame)
        pass


        with CodeGroup():
            vbox_input_box = QVBoxLayout()
            frame = QtWidgets.QWidget()
            #frame.setStyleSheet("QWidget {padding: 0px;}")
            frame.setLayout(vbox_input_box)

            label = QLabel("YouSay:")
            vbox_input_box.addWidget(label)

            self.input_box = QTextEdit()
            self.input_box.setMinimumHeight(50)
            vbox_input_box.addWidget(self.input_box)

            splitter.addWidget(frame)
        pass

        with CodeGroup():
            hbox_buttons = QHBoxLayout()
            self.send_button = QPushButton("Send")
            self.send_button.clicked.connect(self.on_send_button_clicked)
            hbox_buttons.addWidget(self.send_button)
            vbox.addLayout(hbox_buttons)
        pass

        splitter.setSizes([700, 100])
        self.setLayout(vbox)

        return


    def on_send_button_clicked(self):
        usermsg = self.input_box.toPlainText()
        usermsg = usermsg.strip()
        if usermsg == '': return
        self.input_box.setPlainText("")

        self.send_button.setEnabled(False)  # 置为不可用
        self.send_button.setText('Sending ...')
        self.chat_box.append("===================================================================")
        self.chat_box.append("YouSay[{}]: {}".format(ChatContext.username, usermsg))
        self.chat_box.append("-------------------------------------------------------------------")
        threading.Thread(target=self.handle_message, args=(usermsg,)).start()
        #self.handle_message(usermsg)

        self.timeoutCoundown = ChatContext.timeout
        self.timeoutTimer.start(1000)
        self.timeoutTimer.timeout.connect(self.on_timeout_timer)
        return
        

    def on_timeout_timer(self):
        self.timeoutCoundown -= 1
        if self.timeoutCoundown <= 0:
            self.timeoutTimer.stop()
            self.send_button.setEnabled(True)  # 置为可用
            self.send_button.setText('Send')
        else:
            self.send_button.setText(f'Sending ...({self.timeoutCoundown})')
        pass
        return


    def handle_message(self, usermsg):
        # 在后台线程中调用 ChatAPI 处理用户输入的消息
        if ChatContext.direct:
            #rspmsg = ChatDebugEcho(usermsg)
            rspmsg = ChatAPI(usermsg)
        else:
            rspmsg = ChatBot(usermsg)
        pass

        self.chat_box.append("ChatGPT: {}".format(rspmsg))
        self.chat_box.append("-------------------------------------------------------------------")
        self.chat_box.verticalScrollBar().setValue(
            self.chat_box.verticalScrollBar().maximum() + 1
        )  # 滚动到底部
        self.send_button.setEnabled(True)  # 置为可用
        self.send_button.setText('Send')
        self.timeoutTimer.stop()
        return
        


def init():
    cmdpath = sys.argv[0]
    basedir = os.path.dirname(cmdpath)
    if basedir == "":
        basedir = os.curdir
    pass

    curtime = datetime.now()
    timestr = curtime.strftime("%Y-%m-%d_%H-%M-%S")
    ChatContext.filepath = basedir + "/log/chat." + timestr + ".log"
    MTFileUtils.MakeSureParentDir(ChatContext.filepath)

    GMTConfig.Load(basedir + "/ChatGPTConsole.ini")

    # host
    ChatContext.host = GMTConfig.GetItemValue("Default", "host")
    if ChatContext.host == "":
        ChatContext.host = "https://127.0.0.1:4540"

    # direct
    ChatContext.direct = GMTConfig.GetItemValue("Default", "direct") == "1"

    # api_key
    openai.api_key = GMTConfig.GetItemValue("Default", "api_key")
    if openai.api_key == "":
        print("api_key is empty")
    pass


if __name__ == "__main__":
    import sys

    init()
    app = QtWidgets.QApplication(sys.argv)

    # Step 1: Get name
    name_dialog = NameDialog()
    if name_dialog.exec() != QtWidgets.QDialog.Accepted:
        sys.exit(-1)

    # Step 2: Start chat
    chat_window = ChatWindow()
    chat_window.show()


    sys.exit(app.exec_())