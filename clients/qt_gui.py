#!/usr/bin/env python

import sys
import logging
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
from PyQt5 import QtCore
from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import Qt, QModelIndex, QAbstractListModel, QUrl

print('Qt version:', QtCore.QT_VERSION_STR)
assert sys.version_info.major == 3

sys.path.insert(0, '../p2p')
from lib.network import Node
from lib.configuration import Configuration


class ContactListWidget(QWidget):
    def __init__(self):
        super().__init__()
        configuration = Configuration()
        self.node = Node(configuration)
        #self.node.run()
        self.cw = ChatWidget()


class ChatLogModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.log = []
        props = ['name', 'msg', 'time']
        self._roles = {Qt.UserRole + 1 + i: 'cl_'+p for (i, p) in enumerate(props)}

    def rowCount(self, parent):
        return len(self.log)

    def data(self, index, role):
        if not index.isValid():
            return
        row, col = index.row(), index.column()
        if role in self._roles.keys():
            pname = self._roles[role]
            pname = pname[3:]
            return self.log[row][pname]

    def roleNames(self):
        return self._roles

    @QtCore.pyqtSlot(str)
    def say(self, txt):
        """ Main function to add things to the log """
        name = "Dog 2"
        tijd='13:37'
        self.addMsg(tijd, name, txt)

    def addMsg(self, tijd, name, txt):
        p = QModelIndex()
        self.beginInsertRows(p, len(self.log), len(self.log))
        self.log.append({'msg': txt, 'name': name, 'time':tijd})
        self.endInsertRows()


class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.log = ChatLogModel()
        self.qw = QQuickView()
        ctx = self.qw.rootContext()
        ctx.setContextProperty('chatlog', self.log)
        self.qw.setSource(QUrl('chat.qml'))
        self.qw.setResizeMode(QQuickView.SizeRootObjectToView)
        w = self.createWindowContainer(self.qw)
        v = QVBoxLayout(self)
        v.addWidget(w)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    #w = ContactListWidget()
    w = ChatWidget()
    w.show()
    w.resize(300, 400)
    app.exec()

