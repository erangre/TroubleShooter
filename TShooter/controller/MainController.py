# import os
# import csv
from sys import platform as _platform
from qtpy import QtWidgets, QtCore
from functools import partial

# import xml.etree.cElementTree as ET

from ..model.tshoot_model import TroubleShooter, SECTION_SOLUTION
from ..widget.MainWidget import MainWidget
from .SectionEditController import SectionEditController
from .SectionViewController import SectionViewController


DEFAULT_IMAGE = ''


class MainController(object):
    """
    Main controller for the troubleshooter
    """

    def __init__(self, use_settings=True):
        self.use_settings = use_settings
        self.widget = MainWidget()
        self.model = TroubleShooter(category_id="main", level=0)
        self.section_edit_controller = SectionEditController(model=self.model, main_widget=self.widget)
        self.section_view_controller = SectionViewController(model=self.model, main_widget=self.widget)

        self.setup_connections()
        self.category_info = {}
        self.section_id = None
        self.choice_click_functions = []

    def setup_connections(self):
        self.widget.add_category_btn.clicked.connect(self.add_category_btn_clicked)
        self.widget.add_section_btn.clicked.connect(self.add_section_btn_clicked)
        self.widget._main_tree.itemSelectionChanged.connect(self.tree_item_selection_changed)

    def show_window(self):
        self.widget.show()

        if _platform == "darwin":
            self.widget.setWindowState(self.widget.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.widget.activateWindow()
            self.widget.raise_()

    def add_category_btn_clicked(self):
        subcat_id = self.category_info.get('id', None)
        subcat_caption = self.category_info.get('caption', None)
        subcat_image = self.category_info.get('image', None)
        parent_id = self.category_info.get('parent_id', None)

        # prevent adding a subcategory in a section
        for tree_item_id, tree_item in self.widget.sections.items():
            if self.widget.get_selected_categories()[0] == tree_item:
                return

        if not parent_id and self.widget.get_selected_categories():
            for tree_item_id, tree_item in self.widget.categories.items():
                if self.widget.get_selected_categories()[0] == tree_item:
                    parent_id = tree_item_id
        if not parent_id:
            parent_id = "main"

        # prevent subcategories being made in category with sections
        for section_id, section in self.widget.sections.items():
            if self.model.get_section_by_id(section_id)['parent_id'] == parent_id:
                return

        if not subcat_id:
            subcat_id, ok = QtWidgets.QInputDialog.getText(self.widget, 'Create a new subcategory', 'Category ID')

            if not ok:
                return
            subcat_caption, ok = QtWidgets.QInputDialog.getText(self.widget, 'Create a new subcategory',
                                                                'Category Caption')
            if not ok:
                return
            subcat_image, _ = QtWidgets.QFileDialog.getOpenFileName(self.widget, None, 'Choose image for subcategory')
            if subcat_image == '':
                subcat_image = DEFAULT_IMAGE

        self.model.add_subcategory(parent_id, subcat_id, subcat_caption, subcat_image)
        if parent_id == "main":
            self.widget.add_category(subcat_id, subcat_caption)
        else:
            self.widget.add_subcategory(parent_id, subcat_id, subcat_caption)

    def add_section_btn_clicked(self):
        section_id = self.section_id

        parent_id = None

        selected_categories = self.widget.get_selected_categories()
        if selected_categories:
            for tree_item_id, tree_item in self.widget.categories.items():
                if selected_categories[0] == tree_item:
                    parent_id = tree_item_id
            if not parent_id:
                for tree_item_id, tree_item in self.widget.sections.items():
                    if selected_categories[0] == tree_item:
                        parent_id = self.model.get_section_by_id(tree_item_id)['parent_id']
        else:
            parent_id = None

        if not parent_id or parent_id == "main":
            return
        # prevent sections being made in category with subcategory
        for category_id, category in self.widget.categories.items():
            if self.model.get_category_by_id(category_id)['parent_id'] == parent_id:
                return

        if section_id is None:
            section_id, ok = QtWidgets.QInputDialog.getText(self.widget, 'Create a new section', 'Section ID')
            if not ok:
                return
        self.model.add_section_to_category(parent_id, section_id, section_id)
        self.widget.add_section(parent_id, section_id)

    def tree_item_selection_changed(self):
        selected_items = self.widget.get_selected_categories()
        if len(selected_items) == 0:
            return
        self.selected_item = selected_items[0]

        if self.selected_item in self.widget.sections.values():
            self.widget._hlayout.addWidget(self.widget.section_edit_pane)
            self.widget.section_edit_pane.setVisible(True)
            self.update_section_edit_pane()
            self.widget._hlayout.addWidget(self.widget.section_view_pane)
            self.widget.section_view_pane.setVisible(True)
            self.update_section_view_pane()
        else:
            self.widget._hlayout.removeWidget(self.widget.section_edit_pane)
            self.widget.section_edit_pane.setVisible(False)
            self.widget._hlayout.removeWidget(self.widget.section_view_pane)
            self.widget.section_view_pane.setVisible(False)

    def update_section_edit_pane(self):
        selected_section = self.model.get_section_by_id(self.selected_item.text(0))
        self.widget.section_edit_pane.section_id_lbl.setText(selected_section['id'])
        self.widget.section_edit_pane.section_caption_le.setText(selected_section['caption'])
        self.widget.section_edit_pane.section_parent_id_le.setText(selected_section['parent_id'])
        self.widget.section_edit_pane.section_level_le.setText(str(selected_section['level']))
        self.widget.section_edit_pane.section_message_list.clear()
        # self.widget.section_edit_pane.section_choice_list.clearContents()  # removed these because they were deleting the header labels
        # self.widget.section_edit_pane.section_choice_list.clear()
        self.widget.section_edit_pane.section_choice_list.setRowCount(0)
        for message in selected_section['messages']:
            self.widget.section_edit_pane.section_message_list.addItem(message)
        for ind in range(0, len(selected_section['choices'])):
            section_choice_list = self.widget.section_edit_pane.section_choice_list
            section_choice_list.insertRow(section_choice_list.rowCount())
            section_choice_list.setItem(section_choice_list.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(
                selected_section['choices'][ind]))
            section_choice_list.setItem(section_choice_list.rowCount() - 1, 1,
                                        QtWidgets.QTableWidgetItem(selected_section['solution_type'][ind]))
            if selected_section['solution_section_id'][ind] is None:
                solution = selected_section['solution_message'][ind]
            else:
                solution = selected_section['solution_section_id'][ind]
            section_choice_list.setItem(section_choice_list.rowCount() - 1, 2, QtWidgets.QTableWidgetItem(solution))

    def update_section_view_pane(self):
        self.widget.section_view_pane.next_section_btn.setEnabled(False)
        self.widget.section_view_pane.next_section_btn.setVisible(False)
        self.widget.section_view_pane.previous_section_btn.setEnabled(False)
        self.widget.section_view_pane.previous_section_btn.setVisible(False)
        self.clear_layout(self.widget.section_view_pane.message_layout)
        self.clear_layout(self.widget.section_view_pane.choices_layout)
        self.widget.section_view_pane.solution_message_lbl.setVisible(False)
        # self.clear_layout(self.widget.section_view_pane.solution_layout)
        selected_section = self.model.get_section_by_id(self.selected_item.text(0))
        self.widget.section_view_pane.section_id_lbl.setText(selected_section['id'])
        self.widget.section_view_pane.section_caption_lbl.setText(selected_section['caption'])
        for msg in selected_section['messages']:
            self.widget.section_view_pane.messages.append(QtWidgets.QLabel(msg))
            self.widget.section_view_pane.message_layout.addWidget(self.widget.section_view_pane.messages[-1])
        for ind in range(0, len(selected_section['choices'])):
            self.widget.section_view_pane.choices.append(QtWidgets.QPushButton(selected_section['choices'][ind]))
            self.choice_click_functions.append(self.create_choice_click_function(selected_section, ind))
            self.widget.section_view_pane.choices[-1].clicked.connect(self.choice_click_functions[-1])
            self.widget.section_view_pane.choices_layout.addWidget(self.widget.section_view_pane.choices[-1])

    def clear_layout(self, layout):
        """
        :param layout:
        :type layout: QtWidgets.QLayout
        :return:
        """
        for ind in reversed(range(layout.count())):
            widget_to_remove = layout.itemAt(ind).widget()
            layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)
            widget_to_remove.deleteLater()

    def create_choice_click_function(self, selected_section, ind):
        if selected_section['solution_type'][ind] == 'message':
            def choice_click_function():
                self.widget.section_view_pane.solution_message_lbl.setText(selected_section['solution_message'][ind])
                self.widget.section_view_pane.solution_message_lbl.setVisible(True)
        elif selected_section['solution_type'][ind] == 'section':
            def choice_click_function():
                self.widget.section_view_pane.solution_message_lbl.setText(SECTION_SOLUTION)
                self.widget.section_view_pane.next_section_btn.setEnabled(True)
                self.widget.section_view_pane.next_section_btn.setVisible(True)
                self.widget.section_view_pane.solution_message_lbl.setVisible(True)
                # self.widget.section_view_pane.next_section_btn.clicked.connect(
                #     partial(self.widget.set_selected_section, selected_section['solution_section_id'][ind]))
                self.widget.section_view_pane.next_section_btn.clicked.connect(
                    self.create_next_btn_clicked_function(selected_section, ind))
        else:
            choice_click_function = None

        return choice_click_function

    def create_next_btn_clicked_function(self, selected_section, ind):
        def next_btn_clicked_function():
            self.widget.set_selected_section(selected_section['solution_section_id'][ind])
            self.widget.section_view_pane.previous_section_btn.clicked.connect(
                partial(self.widget.set_selected_section, selected_section['id']))
            self.widget.section_view_pane.previous_section_btn.setEnabled(True)
            self.widget.section_view_pane.previous_section_btn.setVisible(True)
        return next_btn_clicked_function
