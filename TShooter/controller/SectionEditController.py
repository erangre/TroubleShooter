# import os
# import csv
from sys import platform as _platform
from qtpy import QtWidgets, QtCore

# import xml.etree.cElementTree as ET

from ..model.tshoot_model import TroubleShooter
# from ..widget.SectionEditWidget import SectionEditGroupBox
from ..widget.MainWidget import MainWidget


class SectionEditController(object):
    """
    Class for editing sections
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
        self.widget.section_edit_pane.add_message_btn.clicked.connect(self.add_message_btn_clicked)
        self.widget.section_edit_pane.remove_message_btn.clicked.connect(self.remove_message_btn_clicked)

    def add_message_btn_clicked(self):
        current_section_id = self.widget.section_edit_pane.section_id_lbl.text()
        item_types = ('Text', 'Image')
        message_type, ok = QtWidgets.QInputDialog.getItem(self.widget, "Message Type",
                                                          "Select message type:", item_types, 0, False)
        if not ok:
            return

        if message_type == 'Text':
            message_text, ok = QtWidgets.QInputDialog.getText(self.widget,
                                                              "New Message Text", "Input message text:")
            if not ok:
                return
        elif message_type == 'Image':
            message_text, ok = QtWidgets.QFileDialog.getOpenFileName(self.widget, "Choose Image")
        else:
            return

        if message_text is None or message_text == '':
            return

        self.widget.section_edit_pane.section_message_list.addItem(str(message_text))
        self.model.add_message_to_section(current_section_id, message_text)

    def remove_message_btn_clicked(self):
        selected_items = self.widget.section_edit_pane.section_message_list.selectedItems()
        for item in selected_items:
            row = self.widget.section_edit_pane.section_message_list.row(item)
            self.widget.section_edit_pane.section_message_list.takeItem(row)
