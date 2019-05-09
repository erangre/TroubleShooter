import os
# import csv
import re
from sys import platform as _platform
from qtpy import QtWidgets, QtCore, QtGui
from functools import partial
try:
    import epics
    ep = True
except ImportError:
    ep = False
# import xml.etree.cElementTree as ET

from ..model.tshoot_model import TroubleShooter, SECTION_SOLUTION, IMAGE, TEXT, PV
from ..widget.MainWidget import MainWidget
from .SectionEditController import SectionEditController
from .SectionViewController import SectionViewController
from ..widget.utils import QMsgBoxOKCancel, QMsgBoxNoYes

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
        self.widget.save_tshooter_btn.clicked.connect(self.save_tshooter_btn_clicked)
        self.widget.load_tshooter_btn.clicked.connect(self.load_tshooter_btn_clicked)
        self.widget.clear_tshooter_btn.clicked.connect(self.clear_tshooter_btn_clicked)

        self.widget.add_category_btn.clicked.connect(self.add_category_btn_clicked)
        self.widget.add_section_btn.clicked.connect(self.add_section_btn_clicked)
        self.widget.edit_category_btn.clicked.connect(self.edit_category_btn_clicked)
        self.widget.remove_category_btn.clicked.connect(self.remove_category_btn_clicked)

        self.widget.main_tree.itemSelectionChanged.connect(self.tree_item_selection_changed)
        self.section_edit_controller.section_modified.connect(self.tree_item_selection_changed)

        self.widget.search_le.textChanged.connect(self.search_le_changed)
        self.widget.search_results_table.cellClicked.connect(self.search_results_table_clicked)

    def show_window(self):
        self.widget.show()

        if _platform == "darwin":
            self.widget.setWindowState(self.widget.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            self.widget.activateWindow()
            self.widget.raise_()

    def add_category_btn_clicked(self):
        parent_id = None
        # prevent adding a subcategory in a section
        for tree_item_id, tree_item in self.widget.sections.items():
            if self.widget.get_selected_categories()[0] == tree_item:
                return

        if self.widget.get_selected_categories():
            for tree_item_id, tree_item in self.widget.categories.items():
                if self.widget.get_selected_categories()[0] == tree_item:
                    parent_id = tree_item_id
        if not parent_id:
            parent_id = "main"

        # prevent subcategories being made in category with sections
        for section_id, section in self.widget.sections.items():
            if self.model.get_section_by_id(section_id)['parent_id'] == parent_id:
                return

        subcat_id, ok = QtWidgets.QInputDialog.getText(self.widget, 'Create a new subcategory', 'Category ID')

        if not ok:
            return
        subcat_caption, ok = QtWidgets.QInputDialog.getText(self.widget, 'Create a new subcategory',
                                                            'Category Caption')
        if not ok:
            return
        subcat_image, _ = QtWidgets.QFileDialog.getOpenFileName(self.widget, 'Choose image for subcategory')
        if subcat_image == '':
            subcat_image = DEFAULT_IMAGE

        if self.model.get_category_by_id(subcat_id) or subcat_id == '' or subcat_caption == '':
            return

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
                if selected_categories[0] == tree_item:  # parent is selected category
                    parent_id = tree_item_id
            if not parent_id:
                for tree_item_id, tree_item in self.widget.sections.items():
                    if selected_categories[0] == tree_item:  # parent is selected section's parent category
                        parent_id = self.model.get_section_by_id(tree_item_id)['parent_id']
        else:
            parent_id = None

        if not parent_id or parent_id == "main":  # don't create sections in main
            return
        # prevent sections being made in category with subcategory
        for category_id, category in self.widget.categories.items():
            if self.model.get_category_by_id(category_id)['parent_id'] == parent_id:
                return

        if section_id is None:
            section_id, ok = QtWidgets.QInputDialog.getText(self.widget, 'Create a new section', 'Section ID')
            if not ok:
                return
        if self.model.get_section_by_id(section_id) or section_id == '':
            return
        self.model.add_section_to_category(parent_id, section_id, section_id)
        self.widget.add_section(parent_id, section_id)

    def edit_category_btn_clicked(self):
        selected_categories = self.widget.get_selected_categories()

        if selected_categories:
            for tree_item_id, tree_item in self.widget.categories.items():
                if selected_categories[0] == tree_item:
                    self.edit_category(tree_item_id)
                    return
            for tree_item_id, tree_item in self.widget.sections.items():
                if selected_categories[0] == tree_item:
                    self.edit_section(tree_item_id)
                    return

    def edit_category(self, category_id):
        tree_item = self.widget.categories.get(category_id, None)
        subcat_caption, ok = QtWidgets.QInputDialog.getText(self.widget, 'Edit category',
                                                            'New Category Caption', text=tree_item.text(0))
        if not ok:
            return
        subcat_image, _ = QtWidgets.QFileDialog.getOpenFileName(self.widget, 'Choose new image for subcategory',
                                                                self.model.get_category_by_id(category_id)['image'])
        if subcat_image == '':
            subcat_image = DEFAULT_IMAGE

        if tree_item is not None:
            tree_item.setText(0, subcat_caption)
        self.model.edit_category(category_id, subcat_caption, subcat_image)

    # TODO: currently the caption is taken from the id for sections. This is not the same as for categories. This is why when editing a category it is simple, the id does not change.
    # TODO: when editing a section, the id changes and it makes everything complicated. It also causes the sectoin to move to last place in order. maybe it is better to change this.
    # TODO: to move sections in order it is possible to remove child and add child for the category.
    def edit_section(self, section_id):
        tree_item = self.widget.sections.get(section_id, None)
        new_section_id, ok = QtWidgets.QInputDialog.getText(self.widget, 'Modify section ID', 'Section ID:',
                                                            text=tree_item.text(0))
        if not ok:
            return

        if tree_item is not None:
            tree_item.setText(0, new_section_id)
        parent_id = self.model.get_section_by_id(section_id)['parent_id']
        self.model.edit_section(section_id, new_section_id)
        self.widget.edit_section(parent_id, section_id, new_section_id)

    def remove_category_btn_clicked(self):
        selected_categories = self.widget.get_selected_categories()
        retval = QMsgBoxOKCancel('Are you sure you want to remove ' + selected_categories[0].text(0) + '?')
        if not retval == QtWidgets.QMessageBox.Ok:
            return
        if selected_categories:
            for tree_item_id, tree_item in self.widget.categories.items():
                if selected_categories[0] == tree_item:
                    self.remove_category(tree_item_id)
                    return
            for tree_item_id, tree_item in self.widget.sections.items():
                if selected_categories[0] == tree_item:
                    self.remove_section(tree_item_id)
                    return

    def remove_category(self, category_id):
        temp_subcats = []
        temp_sections = []
        for subcat_id in self.model.get_category_by_id(category_id)['subcategories']:
            temp_subcats.append(subcat_id)
        for section_id in self.model.get_category_by_id(category_id)['sections']:
            temp_sections.append(section_id)

        for subcat_id in temp_subcats:
            self.remove_category(subcat_id)
        for section_id in temp_sections:
            self.remove_section(section_id)

        top_level_tree_item_ind = self.widget.get_index_of_top_level_tree_item(category_id)
        if top_level_tree_item_ind == -1:
            parent_id = self.model.get_category_by_id(category_id)['parent_id']
            self.widget.remove_non_top_level_tree_item(category_id, "category", parent_id)
        else:
            self.widget.remove_top_level_tree_item(category_id, top_level_tree_item_ind)

        self.model.remove_category(category_id)
        del temp_sections
        del temp_subcats

    def remove_section(self, section_id):
        parent_id = self.model.get_section_by_id(section_id)['parent_id']
        self.widget.remove_non_top_level_tree_item(section_id, "section", parent_id)
        self.model.remove_section(section_id)

    def clear_tshooter_btn_clicked(self):
        retval = QMsgBoxOKCancel("Are you sure you want to clear all categories and sections? (there is no undo)")
        if not retval == QtWidgets.QMessageBox.Ok:
            return
        temp_cats = []
        for tree_item_id, tree_item in self.widget.categories.items():
            if self.model.get_category_by_id(tree_item_id)['parent_id'] == 'main':
                temp_cats.append(tree_item_id)

        for tree_item_id in temp_cats:
            self.remove_category(tree_item_id)
        del temp_cats

    def tree_item_selection_changed(self):
        selected_items = self.widget.get_selected_categories()
        if len(selected_items) == 0:
            return
        self.selected_item = selected_items[0]

        if self.selected_item in self.widget.sections.values():
            self.widget._hlayout.addWidget(self.widget.section_edit_pane)
            if not self.widget.view_mode:
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
        self.widget.section_view_pane.choices = []
        self.clear_layout(self.widget.section_view_pane.message_layout)
        self.clear_layout(self.widget.section_view_pane.choices_layout)
        self.widget.section_view_pane.solution_message_lbl.setVisible(False)
        # self.clear_layout(self.widget.section_view_pane.solution_layout)
        selected_section = self.model.get_section_by_id(self.selected_item.text(0))
        self.widget.section_view_pane.section_id_lbl.setText(selected_section['id'])
        self.widget.section_view_pane.section_caption_lbl.setText(selected_section['caption'])
        for msg, msg_type, pv in zip(selected_section['messages'], selected_section['message_type'],
                                     selected_section['message_pv']):
            if msg_type == TEXT:
                msg = self.format_msg(msg)
                if self.model.search_string:
                    msg = self.highlight_msg(msg, self.model.search_string)

            if ep and msg_type == PV:
                msg = self.highlight_msg(msg, '{}')
                msg = msg.format(epics.caget(pv, as_string=True))
            self.widget.section_view_pane.messages.append(QtWidgets.QLabel(msg))
            if msg_type == TEXT:
                self.widget.section_view_pane.message_layout.addWidget(self.widget.section_view_pane.messages[-1])
                self.widget.section_view_pane.messages[-1].setWordWrap(True)
            elif msg_type == IMAGE:
                self.widget.section_view_pane.messages[-1].setPixmap(QtGui.QPixmap(msg))
                self.widget.section_view_pane.message_layout.addWidget(self.widget.section_view_pane.messages[-1])
            elif msg_type == PV:
                self.widget.section_view_pane.message_layout.addWidget(self.widget.section_view_pane.messages[-1])
        for ind in range(0, len(selected_section['choices'])):
            self.widget.section_view_pane.choices.append(QtWidgets.QPushButton(selected_section['choices'][ind]))
            self.choice_click_functions.append(self.create_choice_click_function(selected_section, ind))
            self.widget.section_view_pane.choices[-1].clicked.connect(self.choice_click_functions[-1])
            self.widget.section_view_pane.choices_layout.addWidget(self.widget.section_view_pane.choices[-1])

    def format_msg(self, msg):
        return msg.replace('\\n', '\n').replace('\\t', '\t')

    def highlight_msg(self, msg, search_string):
        non_case_sensitive_msg = re.compile(re.escape(search_string), re.IGNORECASE)
        return str(non_case_sensitive_msg.sub("<b><font color='yellow'>"+search_string.lower()+"</font></b>", msg))

    def clear_layout(self, layout):
        """
        :param layout:
        :type layout: QtWidgets.QLayout
        :return:
        """
        for ind in reversed(range(layout.count())):
            widget_to_remove = layout.itemAt(ind).widget()
            widget_to_remove.hide()
            layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)
            widget_to_remove.deleteLater()

    def create_choice_click_function(self, selected_section, ind):
        if selected_section['solution_type'][ind] == 'message':
            def choice_click_function():
                msg = selected_section['solution_message'][ind]
                if self.model.search_string:
                    msg = self.highlight_msg(msg, self.model.search_string)
                msg = self.format_msg(msg)
                self.widget.section_view_pane.solution_message_lbl.setText(msg)
                self.widget.section_view_pane.solution_message_lbl.setVisible(True)
        elif selected_section['solution_type'][ind] == 'section':
            def choice_click_function():
                # self.widget.section_view_pane.solution_message_lbl.setText(SECTION_SOLUTION)
                # self.widget.section_view_pane.next_section_btn.setEnabled(True)
                # self.widget.section_view_pane.next_section_btn.setVisible(True)
                # self.widget.section_view_pane.solution_message_lbl.setVisible(True)
                # # self.widget.section_view_pane.next_section_btn.clicked.connect(
                # #     partial(self.widget.set_selected_section, selected_section['solution_section_id'][ind]))
                self.widget.set_selected_section(selected_section['solution_section_id'][ind])
                self.widget.section_view_pane.previous_section_btn.clicked.connect(
                    partial(self.widget.set_selected_section, selected_section['id']))
                self.widget.section_view_pane.previous_section_btn.setEnabled(True)
                self.widget.section_view_pane.previous_section_btn.setVisible(True)
                # self.widget.section_view_pane.next_section_btn.clicked.connect(
                #     self.create_next_btn_clicked_function(selected_section, ind))
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

    def save_tshooter_btn_clicked(self):

        filename, ok = QtWidgets.QFileDialog.getSaveFileName(self.widget,
                                                             'Enter a filename for saving troubleshooter data')

        if not filename:
            return
        self.model.export_category_to_yaml(filename)

    def load_tshooter_btn_clicked(self):
        tshooter_file, _ = QtWidgets.QFileDialog.getOpenFileName(self.widget, caption='Choose troubleshooter to open')
        if not tshooter_file or not tshooter_file[0]:
            return
        self.clear_tshooter_btn_clicked()  # first clear everything
        open_in_edit_mode = QMsgBoxNoYes("Open file in Edit Mode")

        self.model.import_category_from_yaml(tshooter_file)
        all_data = self.model.get_all_data()
        self.widget.main_tree.blockSignals(True)
        for category_id in all_data['all_categories']:
            category = all_data['all_categories'][category_id]
            if category['id'] == 'main':
                continue
            if category['parent_id'] == "main":
                self.widget.add_category(category['id'], category['caption'])
            else:
                self.widget.add_subcategory(category['parent_id'], category['id'], category['caption'])
        for section_id in all_data['all_sections']:
            section = all_data['all_sections'][section_id]
            self.widget.add_section(section['parent_id'], section_id)

        if not open_in_edit_mode == QtWidgets.QMessageBox.Yes:
            self.widget.set_selected_category('main')
            self.widget.switch_to_view_mode()
            self.widget.clear_grid_view()
            self.populate_grid_view('main')
        self.widget.main_tree.blockSignals(False)

    def search_le_changed(self, new_search_string):
        self.model.search_string = new_search_string
        if new_search_string == '':
            self.widget.toggle_search_mode(False)
        else:
            self.widget.toggle_search_mode(True)
            self.populate_search_results(new_search_string)

    def populate_search_results(self, search_string):
        search_results = self.model.find_search_string_in_all(search_string)
        self.widget.search_results_table.blockSignals(True)
        self.widget.search_results_table.clearContents()
        self.widget.search_results_table.setRowCount(0)
        for search_result in search_results:
            current_rows = self.widget.search_results_table.rowCount()
            self.widget.search_results_table.setRowCount(current_rows + 1)
            search_result_id = QtWidgets.QTableWidgetItem(search_result['id'])
            search_result_id.setFlags(search_result_id.flags() & ~QtCore.Qt.ItemIsEditable)
            self.widget.search_results_table.setItem(current_rows, 0, search_result_id)
            search_result_text = QtWidgets.QTableWidgetItem(search_result['text'])
            search_result_text.setFlags(search_result_text.flags() & ~QtCore.Qt.ItemIsEditable)
            self.widget.search_results_table.setItem(current_rows, 1, search_result_text)
            search_result_type = QtWidgets.QTableWidgetItem(search_result['type'])
            search_result_type.setFlags(search_result_type.flags() & ~QtCore.Qt.ItemIsEditable)
            self.widget.search_results_table.setItem(current_rows, 2, search_result_type)
            self.widget.search_results_table.horizontalHeader().setSectionResizeMode(1,
                QtWidgets.QHeaderView.ResizeToContents)
        self.widget.search_results_table.blockSignals(False)

    def search_results_table_clicked(self, *args):
        # TODO: maybe add highlight in the table for the searched word. Seems like this requires creating QLabels and
        # TODO: adding them as widgets to the table.
        section_id = str(self.widget.search_results_table.item(args[0], 0).text())
        self.widget.set_selected_section(section_id)

    def populate_grid_view(self, category_id):
        self.widget.category_view_back_btn.setVisible(not (category_id == 'main' or category_id == 'Main'))

        parent_id = self.model.get_category_by_id(category_id)['parent_id']
        try:
            self.widget.category_view_back_btn.clicked.disconnect()
        except TypeError:
            pass
        self.widget.category_view_back_btn.clicked.connect(self.create_category_view_back_btn_clicked_function(
            parent_id))

        sub_cats = self.model.get_category_by_id(category_id)['subcategories']
        if sub_cats:
            for sub_cat_id in sub_cats:
                sub_cat = self.model.get_category_by_id(sub_cat_id)
                caption = sub_cat['caption']
                # if not (caption == 'Main' or caption == 'main'):
                image = sub_cat['image']
                self.widget.add_category_grid_btn(caption, image)
                self.widget.get_last_category_btn().clicked.connect(partial(self.grid_view_subcat_btn_clicked,
                                                                            sub_cat_id))

        sections = self.model.get_category_by_id(category_id)['sections']
        if sections:
            for section_id in sections:
                section = self.model.get_section_by_id(section_id)
                caption = section['caption']
                image = None
                self.widget.add_category_grid_btn(caption, image)
                self.widget.get_last_category_btn().clicked.connect(partial(self.grid_view_section_btn_clicked,
                                                                            section_id))

    def grid_view_subcat_btn_clicked(self, category_id):
        self.widget.clear_grid_view()
        self.populate_grid_view(category_id)

    def grid_view_section_btn_clicked(self, section_id):
        self.widget.set_selected_section(section_id)

    def create_category_view_back_btn_clicked_function(self, category_id):
        def category_view_back_btn_clicked():
            self.widget.clear_grid_view()
            self.populate_grid_view(category_id)
        return category_view_back_btn_clicked
