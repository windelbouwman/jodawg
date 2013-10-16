
import sys

from PyQt4.QtGui import QWidget, QApplication, QVBoxLayout, QHBoxLayout
from PyQt4.QtGui import QLineEdit, QPushButton, QTextEdit
from PyQt4.QtCore import Qt

# TODO: import chatlib?


class ContactListWidget(QWidget):
    def __init__(self):
        super().__init__()


class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self)
        self.log = QTextEdit()
        v.addWidget(self.log)
        h = QHBoxLayout(self)
        v.addLayout(h)
        self.messageEdit = QLineEdit()
        h.addWidget(self.messageEdit)
        self.sendButton = QPushButton()
        self.sendButton.setText("Send")
        h.addWidget(self.sendButton)
        self.sendButton.clicked.connect(self.doSend)
        self.messageEdit.returnPressed.connect(self.doSend)

    def doSend(self):
        txt = self.messageEdit.text()
        self.messageEdit.clear()
        assert type(txt) is str
        print(txt)
        # TODO: transmit text :)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #w = ContactListWidget()
    w = ChatWidget()
    w.show()
    app.exec()

