import sys
import os
import time

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import traceback
from qtpy import QtWidgets


def excepthook(exc_type, exc_value, traceback_obj):
    """
    Global function to catch unhandled exceptions. This function will result in an error dialog which displays the
    error information.

    :param exc_type: exception type
    :param exc_value: exception value
    :param traceback_obj: traceback object
    :return:
    """

    traceback.print_tb(traceback_obj, None)
    traceback.print_exception(exc_type, exc_value, traceback_obj)


def main():
    app = QtWidgets.QApplication([])
    sys.excepthook = excepthook
    from sys import platform as _platform
    from .controller.MainController import MainController

    if _platform == "linux" or _platform == "linux2" or _platform == "win32" or _platform == 'cygwin':
        app.setStyle('plastique')

    controller = MainController()
    controller.show_window()
    app.exec_()
    del app
