# import os
# import csv
from sys import platform as _platform
from qtpy import QtWidgets, QtCore

# import xml.etree.cElementTree as ET

from ..model.tshoot_model import TroubleShooter, SOLUTION_TYPES
# from ..widget.SectionEditWidget import SectionEditGroupBox
from ..widget.MainWidget import MainWidget


class SectionViewController(object):
    """
    Class for Viewing sections
    """

    def __init__(self, model=None, main_widget=None):
        """
        :param model: Reference to the main model
        :param main_widget: Reference to the main widget

        :type model: TroubleShooter
        :type main_widget: MainWidget
        """
        self.widget = main_widget
        self.model = model
        self.setup_connections()

    def setup_connections(self):
        pass
