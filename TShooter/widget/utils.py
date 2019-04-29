from qtpy import QtWidgets, QtCore, QtGui


def QMsgBoxOKCancel(msg_text):
    msg = QtWidgets.QMessageBox()
    msg.setText(msg_text)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
    retval = msg.exec_()
    return retval


def QMsgBoxNoYes(msg_text):
    msg = QtWidgets.QMessageBox()
    msg.setText(msg_text)
    msg.setStandardButtons(QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
    retval = msg.exec_()
    return retval
