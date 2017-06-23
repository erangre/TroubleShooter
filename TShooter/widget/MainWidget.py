from collections import OrderedDict
import os

from qtpy import QtWidgets, QtCore

from .SectionEditWidget import SectionEditGroupBox
from .SectionViewWidget import SectionViewPage

widget_path = os.path.dirname(__file__)


class MainWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)

        self.create_widgets()
        self.arrange_layout()
        self.set_stylesheet()

        self.categories = OrderedDict()
        self.sections = OrderedDict()

        self.add_category("main", "Main")

    def create_widgets(self):
        self.save_tshooter_btn = QtWidgets.QPushButton('Save')
        self.load_tshooter_btn = QtWidgets.QPushButton('Load')
        self.clear_tshooter_btn = QtWidgets.QPushButton('Clear')

        self.add_category_btn = QtWidgets.QPushButton('Add Category')
        self.add_section_btn = QtWidgets.QPushButton('Add Section')
        self.remove_category_btn = QtWidgets.QPushButton('Remove')

        self._main_tree = QtWidgets.QTreeWidget()
        self._main_tree.setColumnCount(2)
        self._main_tree.setHeaderLabels(["caption", "type"])

        self.section_edit_pane = SectionEditGroupBox()
        self.section_edit_pane.setVisible(False)

        self.section_view_pane = SectionViewPage()
        self.section_view_pane.setVisible(False)

    def arrange_layout(self):
        self._file_layout = QtWidgets.QHBoxLayout()
        self._btn_category_layout = QtWidgets.QHBoxLayout()
        self._hlayout = QtWidgets.QHBoxLayout()
        self._category_layout = QtWidgets.QVBoxLayout()

        self._file_layout.addWidget(self.save_tshooter_btn)
        self._file_layout.addWidget(self.load_tshooter_btn)
        self._file_layout.addWidget(self.clear_tshooter_btn)

        self._btn_category_layout.addWidget(self.add_category_btn)
        self._btn_category_layout.addWidget(self.add_section_btn)
        self._btn_category_layout.addWidget(self.remove_category_btn)

        self._category_layout.addLayout(self._file_layout)
        self._category_layout.addLayout(self._btn_category_layout)
        self._category_layout.addWidget(self._main_tree)
        self._hlayout.addLayout(self._category_layout)
        self._hlayout.addWidget(self.section_edit_pane)
        self._hlayout.addWidget(self.section_view_pane)

        self.setLayout(self._hlayout)

    def set_stylesheet(self):
        file = open(os.path.join(widget_path, "stylesheet.qss"))
        stylesheet = file.read()
        self.setStyleSheet(stylesheet)
        file.close()

    def add_category(self, subcat_id, subcat_caption):
        self.categories[subcat_id] = QtWidgets.QTreeWidgetItem()
        self.categories[subcat_id].setText(0, subcat_caption)
        self.categories[subcat_id].setText(1, "category")
        self._main_tree.addTopLevelItem(self.categories[subcat_id])
        self._main_tree.setCurrentItem(self.categories[subcat_id])

    def add_subcategory(self, parent_id, subcat_id, subcat_caption):
        self.categories[subcat_id] = QtWidgets.QTreeWidgetItem()
        self.categories[subcat_id].setText(0, subcat_caption)
        self.categories[subcat_id].setText(1, "sub-category")
        self.categories[parent_id].addChild(self.categories[subcat_id])
        self._main_tree.setCurrentItem(self.categories[subcat_id])

    def remove_top_level_tree_item(self, category_id, tree_item_ind):
        self._main_tree.takeTopLevelItem(tree_item_ind)
        del self.categories[category_id]

    def remove_non_top_level_tree_item(self, tree_item_id, tree_item_type, parent_id):
        if tree_item_type == "category":
            tree_item = self.categories[tree_item_id]
            self.categories[parent_id].removeChild(tree_item)
            del self.categories[tree_item_id]
        elif tree_item_type == "section":
            tree_item = self.sections[tree_item_id]
            self.categories[parent_id].removeChild(tree_item)
            del self.sections[tree_item_id]

    def get_index_of_top_level_tree_item(self, tree_item_id):
        return self._main_tree.indexOfTopLevelItem(self.categories[tree_item_id])

    def get_selected_categories(self):
        return self._main_tree.selectedItems()

    def set_selected_category(self, category_id):
        self._main_tree.setCurrentItem(self.categories[category_id])

    def add_section(self, parent_id, section_id):
        self.sections[section_id] = QtWidgets.QTreeWidgetItem()
        self.sections[section_id].setText(0, section_id)
        self.sections[section_id].setText(1, "section")
        self.categories[parent_id].addChild(self.sections[section_id])
        self._main_tree.setCurrentItem(self.sections[section_id])

    def set_selected_section(self, section_id):
        self._main_tree.setCurrentItem(self.sections[section_id])
