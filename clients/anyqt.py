import sys
import logging

try:
    from PyQt5 import QtCore
    from PyQt5 import QtWidgets
    from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
    from PyQt5 import QtQuick
    from PyQt5.QtCore import Qt, QModelIndex, QAbstractListModel, QUrl
except ImportError:
    from PyQt4 import QtCore

logging.info('Qt version:', QtCore.QT_VERSION_STR)
assert sys.version_info.major == 3

