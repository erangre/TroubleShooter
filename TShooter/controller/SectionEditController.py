import os
# import csv
from sys import platform as _platform
from qtpy import QtWidgets, QtCore

# import xml.etree.cElementTree as ET

from ..model.tshoot_model import TroubleShooter, SOLUTION_TYPES, TEXT, IMAGE, PV
# from ..widget.SectionEditWidget import SectionEditGroupBox
from ..widget.MainWidget import MainWidget


class SectionEditController(QtCore.QObject):
    """
    Class for editing sections
    """
    section_modified = QtCore.Signal()

    def __init__(self, model=None, main_widget=None):
        """
        :param model: Reference to the main model
        :param main_widget: Reference to the main widget

        :type model: TroubleShooter
        :type main_widget: MainWidget
        """
        super(SectionEditController, self).__init__()
        self.widget = main_widget
        self.model = model
        self.setup_connections()

    def setup_connections(self):
        self.widget.section_edit_pane.add_message_btn.clicked.connect(self.add_message_btn_clicked)
        self.widget.section_edit_pane.remove_message_btn.clicked.connect(self.remove_message_btn_clicked)
        self.widget.section_edit_pane.add_choice_btn.clicked.connect(self.add_choice_btn_clicked)
        self.widget.section_edit_pane.remove_choice_btn.clicked.connect(self.remove_choice_btn_clicked)
        self.widget.section_edit_pane.section_message_list.itemDoubleClicked.connect(
            self.section_message_list_dbl_clicked)
        self.widget.section_edit_pane.move_message_up_btn.clicked.connect(self.move_message_up_btn_clicked)
        self.widget.section_edit_pane.move_message_down_btn.clicked.connect(self.move_message_down_btn_clicked)
        self.widget.section_edit_pane.section_choice_list.itemDoubleClicked.connect(
            self.section_choice_list_dbl_clicked)
        self.widget.section_edit_pane.move_choice_up_btn.clicked.connect(self.move_choice_up_btn_clicked)
        self.widget.section_edit_pane.move_choice_down_btn.clicked.connect(self.move_choice_down_btn_clicked)

    def add_message_btn_clicked(self):
        current_section_id = self.widget.section_edit_pane.section_id_lbl.text()
        item_types = ('Text', 'Image', 'PV_string')
        message_type, ok = QtWidgets.QInputDialog.getItem(self.widget, "Message Type",
                                                          "Select message type:", item_types, 0, False)
        if not ok:
            return

        if message_type == 'Text':
            message_text, ok = QtWidgets.QInputDialog.getText(self.widget,
                                                              "New Message Text", "Input message text:")
            if not ok:
                return
            msg_type = TEXT
            pv = None
        elif message_type == 'Image':
            message_text, ok = QtWidgets.QFileDialog.getOpenFileName(self.widget, "Choose Image")
            msg_type = IMAGE
            pv = None
        elif message_type == 'PV_string':
            user_msg = "Input message, using {} as a placeholder for the PV value:"
            message_text, ok = QtWidgets.QInputDialog.getText(self.widget, "New PV string", user_msg)
            if not ok:
                return
            pv, ok = QtWidgets.QInputDialog.getText(self.widget, "New PV", "Please input the PV to read")
            if not ok:
                return
            msg_type = PV

        else:
            return

        if self.is_message_text_bad(message_text, current_section_id):
            return

        self.widget.section_edit_pane.section_message_list.addItem(str(message_text))
        self.model.add_message_to_section(current_section_id, message_text, msg_type, pv)
        self.section_modified.emit()

    def is_message_text_bad(self, message_text, current_section_id):
        if message_text is None or message_text == '' or \
                        message_text in self.model.get_section_by_id(current_section_id)['messages']:
            return True
        else:
            return False

    def remove_message_btn_clicked(self):
        selected_items = self.widget.section_edit_pane.section_message_list.selectedItems()
        current_section_id = self.widget.section_edit_pane.section_id_lbl.text()
        for item in selected_items:
            row = self.widget.section_edit_pane.section_message_list.row(item)
            self.widget.section_edit_pane.section_message_list.takeItem(row)
            self.model.remove_message_from_section(current_section_id, row)
        self.section_modified.emit()

    def section_message_list_dbl_clicked(self, list_item):
        row = self.widget.section_edit_pane.section_message_list.row(list_item)
        current_section_id = self.widget.section_edit_pane.section_id_lbl.text()
        current_section = self.model.get_section_by_id(current_section_id)
        msg_type = current_section['message_type'][row]
        if msg_type == TEXT:
            new_message_text, ok = QtWidgets.QInputDialog.getText(self.widget, "New Message Text",
                                                                  "Input new message text:", text=list_item.text())
            if not ok:
                return

            if self.is_message_text_bad(new_message_text, current_section_id):
                return

            self.model.modify_message_in_section(current_section_id, row, new_message_text)
        elif msg_type == IMAGE:
            base_dir = os.path.dirname(list_item.text())
            new_message_text, ok = QtWidgets.QFileDialog.getOpenFileName(self.widget, "Choose Image",
                                                                         directory=base_dir)

            if self.is_message_text_bad(new_message_text, current_section_id):
                return

            self.model.modify_message_in_section(current_section_id, row, new_message_text)
        elif msg_type == PV:
            user_msg = "Input new message, using {} as a placeholder for the PV value:"
            new_message_text, ok = QtWidgets.QInputDialog.getText(self.widget, "New PV string", user_msg,
                                                                  text=list_item.text())
            if not ok:
                return

            if not new_message_text == current_section['messages'][row]:
                if self.is_message_text_bad(new_message_text, current_section_id):
                    return

            old_pv = current_section['message_pv'][row]
            new_pv, ok = QtWidgets.QInputDialog.getText(self.widget, "New PV", "Please input the new PV to read",
                                                        text=old_pv)
            if not ok:
                return
            self.model.modify_message_in_section(current_section_id, row, new_message_text)
            self.model.modify_message_pv_in_section(current_section_id, row, new_pv)
        self.section_modified.emit()

    def move_message_up_btn_clicked(self):
        selected_items = self.widget.section_edit_pane.section_message_list.selectedItems()
        if len(selected_items) == 0:
            return
        current_section_id = self.widget.section_edit_pane.section_id_lbl.text()
        for list_item in selected_items:
            row = self.widget.section_edit_pane.section_message_list.row(list_item)
            self.model.move_message_up(current_section_id, row)

        self.section_modified.emit()

        self.widget.section_edit_pane.section_message_list.setCurrentItem(
            self.widget.section_edit_pane.section_message_list.item(row - 1), QtCore.QItemSelectionModel.Select)

    def move_message_down_btn_clicked(self):
        selected_items = self.widget.section_edit_pane.section_message_list.selectedItems()
        if len(selected_items) == 0:
            return
        current_section_id = self.widget.section_edit_pane.section_id_lbl.text()
        for list_item in selected_items:
            row = self.widget.section_edit_pane.section_message_list.row(list_item)
            self.model.move_message_down(current_section_id, row)

        self.section_modified.emit()

        self.widget.section_edit_pane.section_message_list.setCurrentItem(
            self.widget.section_edit_pane.section_message_list.item(row + 1), QtCore.QItemSelectionModel.Select)

    def add_choice_btn_clicked(self):
        current_section_id = self.widget.section_edit_pane.section_id_lbl.text()
        solution_types = SOLUTION_TYPES

        choice_text, ok = QtWidgets.QInputDialog.getText(self.widget,
                                                         "Add Choice", "Choice text:")
        if not ok or self.is_choice_text_bad(choice_text, current_section_id):
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

        section_choice_list = self.widget.section_edit_pane.section_choice_list
        section_choice_list.insertRow(section_choice_list.rowCount())
        section_choice_list.setItem(section_choice_list.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(choice_text))
        section_choice_list.setItem(section_choice_list.rowCount() - 1, 1, QtWidgets.QTableWidgetItem(solution_type))
        section_choice_list.setItem(section_choice_list.rowCount() - 1, 2, QtWidgets.QTableWidgetItem(solution))
        self.model.add_choice_to_section(current_section_id, choice_text, solution_type=solution_type,
                                         solution=solution)
        self.section_modified.emit()

    def is_choice_text_bad(self, choice_text, current_section_id):
        if choice_text is None or choice_text == '' or \
                        choice_text in self.model.get_section_by_id(current_section_id)['choices']:
            return True
        else:
            return False

    def remove_choice_btn_clicked(self):
        section_choice_list = self.widget.section_edit_pane.section_choice_list
        current_section_id = self.widget.section_edit_pane.section_id_lbl.text()
        selected_rows = section_choice_list.selectionModel().selectedRows()
        if len(selected_rows) > 0:
            for row in selected_rows:
                self.model.remove_choice_from_section(current_section_id, row.row())
                section_choice_list.removeRow(row.row())
        else:
            selected_items = self.widget.section_edit_pane.section_choice_list.selectedItems()
            if len(selected_items) == 0:
                return
            for list_item in selected_items:
                row = self.widget.section_edit_pane.section_choice_list.row(list_item)
                self.model.remove_choice_from_section(current_section_id, row)
        self.section_modified.emit()

    def section_choice_list_dbl_clicked(self, list_item):
        row = self.widget.section_edit_pane.section_choice_list.row(list_item)
        choice_item = self.widget.section_edit_pane.section_choice_list.item(row, 0)
        current_section_id = self.widget.section_edit_pane.section_id_lbl.text()
        current_section = self.model.get_section_by_id(current_section_id)  # type:
        solution_type = current_section['solution_type'][row]

        new_choice_text, ok = QtWidgets.QInputDialog.getText(self.widget,
                                                             "Add Choice", "Choice text:", text=choice_item.text())
        if not ok:
            return

        if not new_choice_text == self.widget.section_edit_pane.section_choice_list.item(row, 0).text():
            if self.is_choice_text_bad(new_choice_text, current_section_id):
                return

        self.model.modify_choice_in_section(current_section_id, row, new_choice_text)
        choice_item.setText(new_choice_text)

        if solution_type == 'message':
            old_message_item = self.widget.section_edit_pane.section_choice_list.item(row, 2)
            new_message_text, ok = QtWidgets.QInputDialog.getText(self.widget, "New Solution Message Text",
                                                                  "Input new solution message text:",
                                                                  text=old_message_item.text())
            if not ok:
                return
            self.model.modify_solution_message_in_section(current_section_id, row, new_message_text)
        elif solution_type == 'section':
            all_sections_formatted = self.model.get_all_sections_formatted()
            new_solution, ok = QtWidgets.QInputDialog.getItem(self.widget, "Next Section",
                                                              "Select next section for " + new_choice_text + ":",
                                                              all_sections_formatted, 0, False)
            solution = new_solution.split(':', 1)[-1]
            self.model.modify_solution_section_in_section(current_section_id, row, solution)

        self.section_modified.emit()

    def move_choice_up_btn_clicked(self):
        selected_items = self.widget.section_edit_pane.section_choice_list.selectedItems()
        if len(selected_items) == 0:
            return
        current_section_id = self.widget.section_edit_pane.section_id_lbl.text()
        for list_item in selected_items:
            row = self.widget.section_edit_pane.section_choice_list.row(list_item)
            self.model.move_choice_up(current_section_id, row)

        self.section_modified.emit()

        self.widget.section_edit_pane.section_choice_list.setCurrentItem(
            self.widget.section_edit_pane.section_choice_list.item(row - 1, 0), QtCore.QItemSelectionModel.Select)

    def move_choice_down_btn_clicked(self):
        selected_items = self.widget.section_edit_pane.section_choice_list.selectedItems()
        if len(selected_items) == 0:
            return
        current_section_id = self.widget.section_edit_pane.section_id_lbl.text()
        for list_item in selected_items:
            row = self.widget.section_edit_pane.section_choice_list.row(list_item)
            self.model.move_choice_down(current_section_id, row)

        self.section_modified.emit()

        self.widget.section_edit_pane.section_choice_list.setCurrentItem(
            self.widget.section_edit_pane.section_choice_list.item(row + 1, 0), QtCore.QItemSelectionModel.Select)
