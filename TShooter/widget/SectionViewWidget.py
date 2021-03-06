from collections import OrderedDict
import os

from qtpy import QtWidgets, QtCore

widget_path = os.path.dirname(__file__)


class SectionViewPage(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(SectionViewPage, self).__init__(*args, **kwargs)
        self.create_widgets()
        self.arrange_section_layout()
        self.set_widget_properties()
        self.messages = []
        self.choices = []

    def create_widgets(self):
        self.section_id_lbl = QtWidgets.QLabel()
        self.section_caption_lbl = QtWidgets.QLabel('')
        self.solution_message_lbl = QtWidgets.QLabel('')
        self.solution_message_lbl.setWordWrap(True)
        self.previous_section_btn = QtWidgets.QPushButton('Previous')
        self.next_section_btn = QtWidgets.QPushButton('Next')

    def set_widget_properties(self):
        self.section_caption_lbl.setStyleSheet("font-size: 18pt;"
                                               "color: lime;")

    def arrange_section_layout(self):
        self._outer_layout = QtWidgets.QVBoxLayout()
        self._main_layout = QtWidgets.QVBoxLayout()
        self.scroll_widget = QtWidgets.QWidget()
        self.scroll = QtWidgets.QScrollArea()
        self.scroll_widget.setLayout(self._main_layout)
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.scroll_widget)

        self._top_nav_layout = QtWidgets.QHBoxLayout()
        self.message_layout = QtWidgets.QVBoxLayout()
        self.choices_layout = QtWidgets.QHBoxLayout()
        self.solution_layout = QtWidgets.QHBoxLayout()
        self._bottom_nav_layout = QtWidgets.QHBoxLayout()

        self.solution_layout.addWidget(self.solution_message_lbl)

        self._bottom_nav_layout.addWidget(self.previous_section_btn)
        self._bottom_nav_layout.addStretch(1)
        self._bottom_nav_layout.addWidget(self.next_section_btn)

        self._main_layout.addLayout(self._top_nav_layout)
        self._main_layout.addWidget(self.section_caption_lbl)
        self._main_layout.addLayout(self.message_layout)
        self._main_layout.addLayout(self.choices_layout)
        self._main_layout.addLayout(self.solution_layout)
        self._main_layout.addStretch(1)
        self._main_layout.addLayout(self._bottom_nav_layout)
        self._outer_layout.addWidget(self.scroll)
        self.setLayout(self._outer_layout)
