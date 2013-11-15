
from anyqt import QtCore, Qt


class ChatLogModel(QtCore.QAbstractListModel):
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
        msg = self.log[row]
        if role in self._roles.keys():
            pname = self._roles[role]
            pname = pname[3:]
            return msg[pname]
        elif role is Qt.DisplayRole:
            return str(msg)

    def roleNames(self):
        return self._roles

    @QtCore.pyqtSlot(str)
    def say(self, txt):
        """ Main function to add things to the log """
        name = "Dog 2"
        tijd='13:37'
        self.addMsg(tijd, name, txt)

    def addMsg(self, tijd, name, txt):
        p = QtCore.QModelIndex()
        self.beginInsertRows(p, len(self.log), len(self.log))
        self.log.append({'msg': txt, 'name': name, 'time':tijd})
        self.endInsertRows()


