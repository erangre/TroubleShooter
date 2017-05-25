from collections import OrderedDict
import os

from qtpy import QtWidgets, QtCore

widget_path = os.path.dirname(__file__)


class SectionEditGroupBox(QtWidgets.QGroupBox):
    def __init__(self, *args, **kwargs):
        super(SectionEditGroupBox, self).__init__(*args, **kwargs)
        self.create_widgets()
        self.arrange_section_layout()

    def create_widgets(self):
        self.section_id_lbl = QtWidgets.QLabel()
        self.section_caption_lbl = QtWidgets.QLabel('Caption')
        self.section_caption_le = QtWidgets.QLineEdit()
        self.section_parent_id_lbl = QtWidgets.QLabel('Parent ID')
        self.section_parent_id_le = QtWidgets.QLineEdit()
        self.section_parent_id_le.setEnabled(False)
        self.section_level_lbl = QtWidgets.QLabel('Level')
        self.section_level_le = QtWidgets.QLineEdit()
        self.section_level_le.setEnabled(False)

        self.message_lbl = QtWidgets.QLabel('Messages to user:')
        self.section_message_list = QtWidgets.QListWidget()
        self.add_message_btn = QtWidgets.QPushButton('+')
        self.remove_message_btn = QtWidgets.QPushButton('-')

        self.choice_lbl = QtWidgets.QLabel('User choices:')
        self.section_choice_list = QtWidgets.QTableWidget()
        self.section_choice_list.setColumnCount(3)
        self.section_choice_list.setHorizontalHeaderLabels(['Choice', 'Solution Type', 'Solution'])
        self.add_choice_btn = QtWidgets.QPushButton('+')
        self.remove_choice_btn = QtWidgets.QPushButton('-')

    def arrange_section_layout(self):
        self._grid_layout = QtWidgets.QGridLayout()

        self._grid_layout.addWidget(self.section_parent_id_lbl, 0, 0, 1, 1)
        self._grid_layout.addWidget(self.section_parent_id_le, 0, 1, 1, 1)
        self._grid_layout.addWidget(self.section_level_lbl, 0, 2, 1, 1)
        self._grid_layout.addWidget(self.section_level_le, 0, 3, 1, 1)
        self._grid_layout.addWidget(self.section_caption_lbl, 1, 0, 1, 1)
        self._grid_layout.addWidget(self.section_caption_le, 1, 1, 1, 3)
        self._grid_layout.addWidget(self.message_lbl, 2, 0, 1, 4)
        self._grid_layout.addWidget(self.section_message_list, 3, 0, 5, 3)
        self._grid_layout.addWidget(self.add_message_btn, 4, 3, 1, 1)
        self._grid_layout.addWidget(self.remove_message_btn, 5, 3, 1, 1)
        self._grid_layout.addWidget(self.choice_lbl, 8, 0, 1, 4)
        self._grid_layout.addWidget(self.section_choice_list, 9, 0, 5, 3)
        self._grid_layout.addWidget(self.add_choice_btn, 10, 3, 1, 1)
        self._grid_layout.addWidget(self.remove_choice_btn, 11, 3, 1, 1)

        self.setLayout(self._grid_layout)
