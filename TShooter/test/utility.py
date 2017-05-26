# -*- coding: utf8 -*-

import unittest
from qtpy import QtWidgets, QtCore
from qtpy.QtTest import QTest
import os

unittest_data_path = os.path.join(os.path.dirname(__file__), 'data')


class QtTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance()
        if cls.app is None:
            cls.app = QtWidgets.QApplication([])


def delete_if_exists(data_path):
    if os.path.exists(data_path):
        os.remove(data_path)


def click_button(widget):
    QTest.mouseClick(widget, QtCore.Qt.LeftButton)


def click_checkbox(checkbox_widget):
    QTest.mouseClick(checkbox_widget, QtCore.Qt.LeftButton,
                     pos=QtCore.QPoint(2, checkbox_widget.height() / 2.0))


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
