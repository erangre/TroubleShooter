from collections import OrderedDict
import os

from qtpy import QtWidgets, QtCore, QtGui

from .SectionEditWidget import SectionEditGroupBox
from .SectionViewWidget import SectionViewPage

widget_path = os.path.dirname(__file__)


class MainWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)

        self.create_widgets()
        self.arrange_layout()
        self.set_stylesheet()

        self.categories = OrderedDict()  # type: dict[str, QtWidgets.QTreeWidgetItem]
        self.sections = OrderedDict()  # type: dict[str, QtWidgets.QTreeWidgetItem]

        self.add_category("main", "Main")

        self.view_mode = False
        self._category_grid_btns = []  # type: list[QtWidgets.QPushButton]

    def create_widgets(self):
        self.save_tshooter_btn = QtWidgets.QPushButton('Save')
        self.load_tshooter_btn = QtWidgets.QPushButton('Load')
        self.clear_tshooter_btn = QtWidgets.QPushButton('Clear')

        self.add_category_btn = QtWidgets.QPushButton('Add Category')
        self.add_section_btn = QtWidgets.QPushButton('Add Section')
        self.edit_category_btn = QtWidgets.QPushButton('Edit')
        self.remove_category_btn = QtWidgets.QPushButton('Remove')
        self.move_tree_item_up_btn = QtWidgets.QPushButton(u'\u2191')
        self.move_tree_item_down_btn = QtWidgets.QPushButton(u'\u2193')

        self.main_tree = QtWidgets.QTreeWidget()
        self.main_tree.setColumnCount(2)
        self.main_tree.setHeaderLabels(["caption", "type"])

        self.search_le = QtWidgets.QLineEdit('')
        self.category_view_back_btn = QtWidgets.QPushButton('Back')
        self.category_view_back_btn.setVisible(False)

        self.search_results_table = QtWidgets.QTableWidget()
        self.search_results_table.setColumnCount(3)
        self.search_results_table.setHorizontalHeaderLabels(['section_id', 'Text', 'Type'])
        self.search_results_table.horizontalHeader().setVisible(True)
        self.search_results_table.horizontalHeader().setStretchLastSection(False)

        self.section_edit_pane = SectionEditGroupBox()

        self.section_edit_pane.setVisible(False)

        self.section_view_pane = SectionViewPage()
        self.section_view_pane.setVisible(False)

        self.edit_category_frame = QtWidgets.QFrame()
        self.view_category_frame = QtWidgets.QFrame()
        self.view_category_frame.setVisible(False)
        self.search_results_frame = QtWidgets.QFrame()
        self.search_results_frame.setVisible(False)

    def arrange_layout(self):
        self._file_layout = QtWidgets.QHBoxLayout()
        self._category_edit_btns_layout = QtWidgets.QHBoxLayout()
        self._hlayout = QtWidgets.QHBoxLayout()
        self._category_edit_layout = QtWidgets.QVBoxLayout()
        self._category_view_layout = QtWidgets.QVBoxLayout()
        self._category_view_grid = QtWidgets.QVBoxLayout()
        self._category_view_grid_scroll_widget = QtWidgets.QWidget()
        self._category_view_grid_scroll = QtWidgets.QScrollArea()

        self._category_view_grid_scroll.setMinimumHeight(900)
        self._category_view_grid_scroll.setMaximumHeight(900)
        self._category_view_grid_scroll_widget.setLayout(self._category_view_grid)
        self._category_view_grid_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self._category_view_grid_scroll.setWidgetResizable(True)
        self._category_view_grid_scroll.setWidget(self._category_view_grid_scroll_widget)
        self._search_results_layout = QtWidgets.QVBoxLayout()

        self._file_layout.addWidget(self.save_tshooter_btn)
        self._file_layout.addWidget(self.load_tshooter_btn)
        self._file_layout.addWidget(self.clear_tshooter_btn)

        self._category_edit_btns_layout.addWidget(self.add_category_btn)
        self._category_edit_btns_layout.addWidget(self.add_section_btn)
        self._category_edit_btns_layout.addWidget(self.edit_category_btn)
        self._category_edit_btns_layout.addWidget(self.remove_category_btn)
        self._category_edit_btns_layout.addWidget(self.move_tree_item_up_btn)
        self._category_edit_btns_layout.addWidget(self.move_tree_item_down_btn)

        self._category_edit_layout.addLayout(self._file_layout)
        self._category_edit_layout.addLayout(self._category_edit_btns_layout)
        self._category_edit_layout.addWidget(self.main_tree)

        self._category_view_layout.addWidget(self.search_le)
        self._category_view_layout.addWidget(self._category_view_grid_scroll)
        self._category_view_layout.addWidget(self.category_view_back_btn)

        self._search_results_layout.addWidget(self.search_results_table)

        self.edit_category_frame.setLayout(self._category_edit_layout)
        self.view_category_frame.setLayout(self._category_view_layout)
        self.search_results_frame.setLayout(self._search_results_layout)

        # self._hlayout.addLayout(self._category_edit_layout)
        self._hlayout.addWidget(self.edit_category_frame)
        self._hlayout.addWidget(self.section_edit_pane)
        self._hlayout.addWidget(self.section_view_pane)

        self.setLayout(self._hlayout)

        self._hlayout.setAlignment(QtCore.Qt.AlignLeft)
        self.view_category_frame.setMinimumWidth(200)
        self.view_category_frame.setMaximumWidth(300)
        self.edit_category_frame.setMinimumWidth(350)
        self.edit_category_frame.setMaximumWidth(350)
        self.search_results_frame.setMinimumWidth(200)
        self.search_results_frame.setMaximumWidth(600)

    def set_stylesheet(self):
        file = open(os.path.normpath(os.path.join(widget_path, "stylesheet.qss")))
        stylesheet = file.read()
        self.setStyleSheet(stylesheet)
        file.close()

    def add_category(self, subcat_id, subcat_caption):
        self.categories[subcat_id] = QtWidgets.QTreeWidgetItem()
        self.categories[subcat_id].setText(0, subcat_caption)
        self.categories[subcat_id].setText(1, "category")
        self.main_tree.addTopLevelItem(self.categories[subcat_id])
        self.main_tree.setCurrentItem(self.categories[subcat_id])

    def add_subcategory(self, parent_id, subcat_id, subcat_caption):
        self.categories[subcat_id] = QtWidgets.QTreeWidgetItem()
        self.categories[subcat_id].setText(0, subcat_caption)
        self.categories[subcat_id].setText(1, "sub-category")
        self.categories[parent_id].addChild(self.categories[subcat_id])
        self.main_tree.setCurrentItem(self.categories[subcat_id])

    def remove_top_level_tree_item(self, category_id, tree_item_ind):
        self.main_tree.takeTopLevelItem(tree_item_ind)
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

    def move_category(self, parent_id, category_id, direction):
        category_ind = self.main_tree.indexFromItem(self.main_tree.selectedItems()[0]).row()
        if parent_id == 'main':
            if direction == 'up':
                if category_ind > 1:
                    category = self.main_tree.takeTopLevelItem(category_ind)
                    self.main_tree.insertTopLevelItem(category_ind - 1, category)
            elif direction == 'down':
                if category_ind < self.main_tree.topLevelItemCount():
                    category = self.main_tree.takeTopLevelItem(category_ind)
                    self.main_tree.insertTopLevelItem(category_ind + 1, category)
        else:
            if direction == 'up':
                if category_ind > 0:
                    category = self.categories[parent_id].takeChild(category_ind)
                    self.categories[parent_id].insertChild(category_ind - 1, category)
            elif direction == 'down':
                if category_ind < self.categories[parent_id].childCount() - 1:
                    category = self.categories[parent_id].takeChild(category_ind)
                    self.categories[parent_id].insertChild(category_ind + 1, category)

    def get_index_of_top_level_tree_item(self, tree_item_id):
        return self.main_tree.indexOfTopLevelItem(self.categories[tree_item_id])

    def get_top_tree_item_count(self):
        return self.main_tree.topLevelItemCount()

    def get_top_level_tree_item_by_index(self, ind):
        return self.main_tree.topLevelItem(ind)

    def get_selected_categories(self):
        return self.main_tree.selectedItems()

    def set_selected_category(self, category_id):
        self.main_tree.setCurrentItem(self.categories[category_id])

    def add_section(self, parent_id, section_id):
        self.sections[section_id] = QtWidgets.QTreeWidgetItem()
        self.sections[section_id].setText(0, section_id)
        self.sections[section_id].setText(1, "section")
        self.categories[parent_id].addChild(self.sections[section_id])
        self.main_tree.setCurrentItem(self.sections[section_id])

    def edit_section(self, parent_id, old_section_id, new_section_id):
        self.categories[parent_id].removeChild(self.sections[old_section_id])
        self.sections = OrderedDict((new_section_id if k == old_section_id else k, v) for k, v in self.sections.items())
        self.categories[parent_id].addChild(self.sections[new_section_id])

    def move_section(self, parent_id, section_id, direction):
        section_ind = self.main_tree.indexFromItem(self.main_tree.selectedItems()[0]).row()
        if direction == 'up':
            if section_ind > 0:
                section = self.categories[parent_id].takeChild(section_ind)
                self.categories[parent_id].insertChild(section_ind - 1, section)
        elif direction == 'down':
            if section_ind < self.categories[parent_id].childCount() - 1:
                section = self.categories[parent_id].takeChild(section_ind)
                self.categories[parent_id].insertChild(section_ind + 1, section)

    def set_selected_section(self, section_id):
        self.main_tree.setCurrentItem(self.sections[section_id])

    def switch_to_view_mode(self):
        self._hlayout.removeWidget(self.edit_category_frame)
        self.edit_category_frame.setVisible(False)
        self._hlayout.insertWidget(0, self.view_category_frame)
        self.view_category_frame.setVisible(True)
        self.add_category_btn.setVisible(False)
        self.add_section_btn.setVisible(False)
        self.remove_category_btn.setVisible(False)
        self.clear_tshooter_btn.setVisible(False)
        self.save_tshooter_btn.setVisible(False)
        self.load_tshooter_btn.setVisible(False)
        self.edit_category_btn.setVisible(False)

        self._hlayout.removeWidget(self.section_edit_pane)
        self.section_edit_pane.setVisible(False)
        self.view_mode = True
        self.fill_view_category_frame('main')

    def toggle_search_mode(self, toggle):
        self.view_category_frame.setVisible(not toggle)
        self.search_results_frame.setVisible(toggle)
        if toggle:
            self._hlayout.removeWidget(self.view_category_frame)
            self._hlayout.insertWidget(0, self.search_results_frame)
            self._search_results_layout.insertWidget(0, self.search_le)
        else:
            self._hlayout.removeWidget(self.search_results_frame)
            self._hlayout.insertWidget(0, self.view_category_frame)
            self._category_view_layout.insertWidget(0, self.search_le)
        self.search_le.setFocus()

    def fill_view_category_frame(self, category_id):

        if category_id == 'main' or category_id == 'Main':
            for ind in range(self.main_tree.topLevelItemCount()):
                top_level_cat = self.main_tree.topLevelItem(ind)
                caption = top_level_cat.text(0)
                if not (caption == 'Main' or caption == 'main'):
                    self._category_grid_btns.append(QtWidgets.QPushButton(caption))
                    self._category_view_grid.addWidget(self._category_grid_btns[-1])
        else:
            current_category_item = self.categories[category_id]
            print(current_category_item)
            for ind in range(current_category_item.childCount()):
                print("adding child number ", ind)
                child_cat = current_category_item.child(ind)
                self._category_grid_btns.append(QtWidgets.QPushButton(child_cat.text(0)))
                self._category_view_grid.addWidget(self._category_grid_btns[-1])

    def clear_grid_view(self):
        self._category_grid_btns = []
        while self._category_view_grid.count():
            child = self._category_view_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def add_category_grid_btn(self, caption, image):
        self._category_grid_btns.append(QtWidgets.QPushButton(caption))
        if image:
            self._category_grid_btns[-1].setIcon(QtGui.QIcon(QtGui.QPixmap(image)))
            self._category_grid_btns[-1].setIconSize(QtCore.QSize(100, 100))
            self._category_grid_btns[-1].setFixedHeight(120)
        self._category_view_grid.addWidget(self._category_grid_btns[-1])

    def get_last_category_btn(self):
        return self._category_grid_btns[-1]
