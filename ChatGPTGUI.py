from PyQt5.QtWidgets import (
    QPushButton,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
)
import threading
from PyQt5 import QtWidgets
from ChatGPTConsole import ChatAPI, ChatContext
import os
from datetime import datetime
import Misc.MTFileUtils as MTFileUtils
from Misc.MTConfigIni import GMTConfig
import openai


class NameDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Your Name")
        self.setFixedSize(300, 100)
        layout = QtWidgets.QVBoxLayout()

        name_label = QtWidgets.QLabel("Your Name:")
        self.name_input = QtWidgets.QLineEdit()
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def accept(self):
        ChatContext.username = self.name_input.text()
        super().accept()


class ChatWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Box")
        self.resize(800, 600)
        self.msg_list = []

        vbox = QVBoxLayout()

        label = QLabel("Welcome, {}".format(ChatContext.username))
        vbox.addWidget(label)

        hbox = QHBoxLayout()

        self.input_box = QLineEdit()
        hbox.addWidget(self.input_box)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.on_send_button_clicked)
        hbox.addWidget(self.send_button)

        vbox.addLayout(hbox)

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        vbox.addWidget(self.chat_box)

        self.setLayout(vbox)

    def on_send_button_clicked(self):
        self.send_button.setEnabled(False)  # 置为不可用
        msg = self.input_box.text()
        self.chat_box.append("You: {}".format(msg))
        threading.Thread(target=self.handle_message, args=(msg,)).start()

    def handle_message(self, msg):
        # 在后台线程中调用 ChatAPI 处理用户输入的消息
        rspmsg = ChatAPI(msg)
        self.chat_box.append("ChatBot: {}".format(rspmsg))
        self.chat_box.append("---")
        self.input_box.setText("")
        self.chat_box.verticalScrollBar().setValue(
            self.chat_box.verticalScrollBar().maximum()
        )  # 滚动到底部
        self.send_button.setEnabled(True)  # 置为可用


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
    direct = GMTConfig.GetItemValue("Default", "direct") == "1"

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
