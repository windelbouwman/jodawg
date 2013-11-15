#!/usr/bin/env python3

import sys
import logging
from anyqt import QtCore, QtWidgets, QtQuick
from chatlogmodel import ChatLogModel

sys.path.insert(0, '../p2p')

from lib.network import Node
from lib.configuration import Configuration


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
        self.log = ChatLogModel()
        self.qw = QtQuick.QQuickView()
        ctx = self.qw.rootContext()
        ctx.setContextProperty('chatlog', self.log)
        self.qw.setSource(QtCore.QUrl('chat.qml'))
        self.qw.setResizeMode(QtQuick.QQuickView.SizeRootObjectToView)
        w = self.createWindowContainer(self.qw)
        v = QtWidgets.QVBoxLayout(self)
        v.addWidget(w)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = QtWidgets.QApplication(sys.argv)
    #w = ContactListWidget()
    w = ChatWidget()
    w.show()
    w.resize(300, 400)
    app.exec()

