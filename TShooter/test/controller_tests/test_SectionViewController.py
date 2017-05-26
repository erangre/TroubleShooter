import os, sys
import gc

# import numpy as np
from qtpy import QtWidgets, QtCore, QtGui
# from qtpy.QtTest import QTest
from mock import MagicMock
from ..utility import QtTest, click_button

from ...controller.MainController import MainController
from ...model.tshoot_model import TroubleShooter
from ...widget.MainWidget import MainWidget
from ..utility import excepthook

unittest_path = os.path.dirname(__file__)
data_path = os.path.join(unittest_path, '../data')


class ViewSectionTests(QtTest):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance()
        if cls.app is None:
            cls.app = QtWidgets.QApplication([])

    def setUp(self):
        # sys.excepthook = excepthook
        self.controller = MainController()
        self.model = self.controller.model
        self.widget = self.controller.widget

        self.cat_id = 'first_category'
        caption = 'The first category!'
        image = os.path.join(data_path, "images/beam_status.png")
        self.controller.category_info = {'id': self.cat_id,
                                         'caption': caption,
                                         'image': image,
                                         }
        self.widget.add_category_btn.click()

        self.section_id = 'section_a'
        self.controller.section_id = self.section_id
        self.widget.add_section_btn.click()

    def tearDown(self):
        del self.controller
        gc.collect()

    def test_selecting_section_adds_section_view_to_layout(self):
        pass
        self.widget.set_selected_category(self.cat_id)

        self.assertFalse(self.helper_is_widget_in_layout(self.widget.section_view_pane,
                                                         self.widget._hlayout))

        self.widget.set_selected_section(self.section_id)

        self.assertTrue(self.helper_is_widget_in_layout(self.widget.section_view_pane,
                                                        self.widget._hlayout))

    def test_selecting_section_updates_section_view_values(self):
        pass
        # self.widget.set_selected_section(self.section_id)
        # current_section = self.model.get_section_by_id(self.section_id)
        # section_caption = current_section['caption']
        # self.assertEqual(self.widget.section_edit_pane.section_caption_le.text(), section_caption)
        #
        # section_parent_id = current_section['parent_id']
        # self.assertEqual(self.widget.section_edit_pane.section_parent_id_le.text(), section_parent_id)
        #
        # section_level = current_section['level']
        # self.assertEqual(self.widget.section_edit_pane.section_level_le.text(), str(section_level))


    def helper_is_widget_in_layout(self, widget, layout):
        for ind in range(layout.count()):
            item = layout.itemAt(ind)
            if item.widget() == widget:
                return True
        return False
