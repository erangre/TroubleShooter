import os
import gc

# import numpy as np
from qtpy import QtWidgets, QtCore
# from qtpy.QtTest import QTest
from mock import MagicMock
from ..utility import QtTest, click_button

from ...controller.MainController import MainController
from ...model.tshoot_model import TroubleShooter
from ...widget.MainWidget import MainWidget

unittest_path = os.path.dirname(__file__)
data_path = os.path.join(unittest_path, '../data')


class EditSectionTests(QtTest):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance()
        if cls.app is None:
            cls.app = QtWidgets.QApplication([])

    def setUp(self):
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

    def test_selecting_section_adds_section_edit_to_layout(self):
        self.widget.set_selected_category(self.cat_id)

        self.assertFalse(self.helper_is_widget_in_layout(self.widget.section_edit_pane,
                                                         self.widget._hlayout))

        self.widget.set_selected_section(self.section_id)

        self.assertTrue(self.helper_is_widget_in_layout(self.widget.section_edit_pane,
                                                        self.widget._hlayout))

    def test_selecting_section_updates_section_edit_values(self):
        self.widget.set_selected_section(self.section_id)
        current_section = self.model.get_section_by_id(self.section_id)
        section_caption = current_section['caption']
        self.assertEqual(self.widget.section_edit_pane.section_caption_le.text(), section_caption)

        section_parent_id = current_section['parent_id']
        self.assertEqual(self.widget.section_edit_pane.section_parent_id_le.text(), section_parent_id)

        section_level = current_section['level']
        self.assertEqual(self.widget.section_edit_pane.section_level_le.text(), str(section_level))

    def test_add_text_message_to_section(self):
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 0)
        message = 'message_1'
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=['Text', True])
        QtWidgets.QInputDialog.getText = MagicMock(return_value=[message, True])
        self.widget.section_edit_pane.add_message_btn.click()
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 1)
        self.assertEqual(self.widget.section_edit_pane.section_message_list.item(0).text(), message)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['messages'][0], message)

    def test_add_image_message_to_section(self):
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 0)
        image_filename = os.path.join(data_path, "images/beam_status.png")
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=['Image', True])
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=[image_filename, ''])
        self.widget.section_edit_pane.add_message_btn.click()
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 1)
        self.assertEqual(self.widget.section_edit_pane.section_message_list.item(0).text(), image_filename)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['messages'][0], image_filename)

    def test_add_and_remove_two_messages_from_section(self):
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=['Text', True])
        QtWidgets.QInputDialog.getText = MagicMock(return_value=['message_1', True])
        self.widget.section_edit_pane.add_message_btn.click()
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 1)

        image_filename = os.path.join(data_path, "images/beam_status.png")
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=['Image', True])
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=[image_filename, ''])
        self.widget.section_edit_pane.add_message_btn.click()
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 2)

        self.widget.section_edit_pane.section_message_list.setCurrentItem(
            self.widget.section_edit_pane.section_message_list.item(1), QtCore.QItemSelectionModel.Select)
        self.widget.section_edit_pane.remove_message_btn.click()
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 1)

        self.widget.section_edit_pane.section_message_list.setCurrentItem(
            self.widget.section_edit_pane.section_message_list.item(0), QtCore.QItemSelectionModel.Select)
        self.widget.section_edit_pane.remove_message_btn.click()
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 0)

    def test_editing_section_updates_model(self):  # maybe this should be in a different test file
        pass

    def helper_is_widget_in_layout(self, widget, layout):
        for ind in range(layout.count()):
            item = layout.itemAt(ind)
            if item.widget() == widget:
                return True
        return False
