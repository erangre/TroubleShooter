# import os
# import csv
from sys import platform as _platform
from qtpy import QtWidgets, QtCore

# import xml.etree.cElementTree as ET

from ..model.tshoot_model import TroubleShooter, SOLUTION_TYPES
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
        self.widget.section_edit_pane.add_choice_btn.clicked.connect(self.add_choice_btn_clicked)

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
        current_section_id = self.widget.section_edit_pane.section_id_lbl.text()
        for item in selected_items:
            row = self.widget.section_edit_pane.section_message_list.row(item)
            self.widget.section_edit_pane.section_message_list.takeItem(row)
            self.model.remove_message_from_section(current_section_id, row)

    def add_choice_btn_clicked(self):
        current_section_id = self.widget.section_edit_pane.section_id_lbl.text()
        solution_types = SOLUTION_TYPES

        choice_text, ok = QtWidgets.QInputDialog.getText(self.widget,
                                                         "Add Choice", "Choice text:")
        if not ok or choice_text == '':
            return
        solution_type, ok = QtWidgets.QInputDialog.getItem(self.widget, "Solution Type",
                                                           "Select Solution type for " + choice_text + ":",
                                                           solution_types, 0, False)
        if not ok:
            return
        if solution_type == 'message':
            solution, ok = QtWidgets.QInputDialog.getText(self.widget,
                                                          "Solution", "Add solution message:")
        elif solution_type == 'section':
            all_sections_formatted = self.model.get_all_sections_formatted()
            solution, ok = QtWidgets.QInputDialog.getItem(self.widget, "Next Section",
                                                          "Select next section for " + choice_text + ":",
                                                          all_sections_formatted, 0, False)
            solution = solution.split(':', 1)[-1]
        else:
            return
        if not ok or solution == '':
            return

        self.widget.section_edit_pane.section_choice_list.addItem(str(choice_text))
        self.model.add_choice_to_section(current_section_id, choice_text, solution_type=solution_type,
                                         solution=solution)
