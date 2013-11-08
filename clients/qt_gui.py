#!/usr/bin/env python

import sys
import logging

try:
    from PyQt5 import QtWidgets, QtCore
except ImportError:
    from PyQt4 import QtGui as QtWidgets
    from PyQt4 import QtCore

print('Qt version:', QtCore.QT_VERSION_STR)
assert sys.version_info.major == 3

sys.path.insert(0, '../p2p')
from lib.network import Node
from lib.configuration import Configuration
logging.basicConfig(level=logging.DEBUG)

class ContactListWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        configuration = Configuration()
        self.node = Node(configuration)
        #self.node.run()
        self.cw = ChatWidget()


class ChatWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        v = QtWidgets.QVBoxLayout(self)
        self.log = QtWidgets.QTextEdit()
        v.addWidget(self.log)
        h = QtWidgets.QHBoxLayout()
        v.addLayout(h)
        self.messageEdit = QtWidgets.QLineEdit()
        h.addWidget(self.messageEdit)
        self.sendButton = QtWidgets.QPushButton()
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
    app = QtWidgets.QApplication(sys.argv)
    #w = ContactListWidget()
    w = ChatWidget()
    w.show()
    app.exec()

