import os, sys
import gc

# import numpy as np
from qtpy import QtWidgets, QtCore, QtGui
# from qtpy.QtTest import QTest
from mock import MagicMock
from ..utility import QtTest, click_button

import epics
import time

from ...controller.MainController import MainController
from ...model.tshoot_model import TroubleShooter, SECTION_SOLUTION
from ...widget.MainWidget import MainWidget
from ..utility import excepthook

unittest_path = os.path.dirname(__file__)
data_path = os.path.join(unittest_path, '../data')


class EditSectionTests(QtTest):
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
        image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
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
        self.helper_create_text_message(message)

        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 1)
        self.assertEqual(self.widget.section_edit_pane.section_message_list.item(0).text(), message)
        self.assertEqual(len(self.model.get_section_by_id(self.section_id)['messages']), 1)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['messages'][0], message)

    def test_add_image_message_to_section(self):
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 0)

        image_filename = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        self.helper_create_image_message(image_filename)

        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 1)
        self.assertEqual(self.widget.section_edit_pane.section_message_list.item(0).text(), image_filename)
        self.assertEqual(len(self.model.get_section_by_id(self.section_id)['messages']), 1)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['messages'][0], image_filename)

    def test_add_pv_message_to_section(self):
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 0)

        message = 'Energy is {0} eV'
        test_value = 37077
        pv = "13IDA:CDEn:E_RBV"
        expected_message = message.format(test_value)
        self.helper_create_pv_message(message, pv)

        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 1)
        self.assertEqual(self.widget.section_edit_pane.section_message_list.item(0).text(), message)
        self.assertEqual(len(self.model.get_section_by_id(self.section_id)['messages']), 1)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['messages'][0], message)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['message_pv'][0], pv)

    def test_add_and_remove_two_messages_from_section(self):
        self.helper_create_text_message('message_1')
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 1)

        image_filename = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        self.helper_create_image_message(image_filename)
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 2)
        self.assertEqual(len(self.model.get_section_by_id(self.section_id)['messages']), 2)

        self.widget.section_edit_pane.section_message_list.setCurrentItem(
            self.widget.section_edit_pane.section_message_list.item(1), QtCore.QItemSelectionModel.Select)
        self.widget.section_edit_pane.remove_message_btn.click()
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 1)
        self.assertEqual(len(self.model.get_section_by_id(self.section_id)['messages']), 1)

        self.widget.section_edit_pane.section_message_list.setCurrentItem(
            self.widget.section_edit_pane.section_message_list.item(0), QtCore.QItemSelectionModel.Select)
        self.widget.section_edit_pane.remove_message_btn.click()
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 0)
        self.assertEqual(len(self.model.get_section_by_id(self.section_id)['messages']), 0)

    def test_edit_text_message(self):
        self.helper_create_text_message('message_1')
        list_item = self.widget.section_edit_pane.section_message_list.item(0)
        self.widget.section_edit_pane.section_message_list.setCurrentItem(
            list_item, QtCore.QItemSelectionModel.Select)

        new_message = 'message_2'
        QtWidgets.QInputDialog.getText = MagicMock(return_value=[new_message, True])
        self.widget.section_edit_pane.section_message_list.itemDoubleClicked.emit(
            list_item)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['messages'][0], new_message)
        self.assertEqual(list_item.text(), new_message)

    def test_edit_image_message(self):
        # sys.excepthook = excepthook
        image_filename = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        self.helper_create_image_message(image_filename)

        list_item = self.widget.section_edit_pane.section_message_list.item(0)
        self.widget.section_edit_pane.section_message_list.setCurrentItem(
            list_item, QtCore.QItemSelectionModel.Select)

        new_image_filename = os.path.normpath(os.path.join(data_path, "images/garfield.png"))
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=[new_image_filename, ''])
        self.widget.section_edit_pane.section_message_list.itemDoubleClicked.emit(
            list_item)
        time.sleep(0.2)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['messages'][0], new_image_filename)
        self.assertEqual(list_item.text(), new_image_filename)

    def test_edit_pv_message(self):
        message = 'Energy is {0} eV'
        pv = "13IDA:CDEn:E_RBV"
        self.helper_create_pv_message(message, pv)

        list_item = self.widget.section_edit_pane.section_message_list.item(0)
        self.widget.section_edit_pane.section_message_list.setCurrentItem(
            list_item, QtCore.QItemSelectionModel.Select)

        new_message = 'Wavelength is {0} A'
        new_pv = "13IDA:CDEn:WL_RBV"
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[new_message, True], [new_pv, True]])
        self.widget.section_edit_pane.section_message_list.itemDoubleClicked.emit(
            list_item)

        self.assertEqual(self.model.get_section_by_id(self.section_id)['messages'][0], new_message)
        self.assertEqual(list_item.text(), new_message)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['message_pv'][0], new_pv)

    def test_move_message_up(self):
        message = "message_1"
        self.helper_create_text_message(message)

        image_filename = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        self.helper_create_image_message(image_filename)

        list_item = self.widget.section_edit_pane.section_message_list.item(1)
        self.widget.section_edit_pane.section_message_list.setCurrentItem(
            list_item, QtCore.QItemSelectionModel.Select)

        self.widget.section_edit_pane.move_message_up_btn.click()
        list_item = self.widget.section_edit_pane.section_message_list.item(0)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['messages'][0], image_filename)
        self.assertEqual(list_item.text(), image_filename)

    def test_move_message_down(self):
        message = "message_1"
        self.helper_create_text_message(message)

        image_filename = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        self.helper_create_image_message(image_filename)

        list_item = self.widget.section_edit_pane.section_message_list.item(0)
        self.widget.section_edit_pane.section_message_list.setCurrentItem(
            list_item, QtCore.QItemSelectionModel.Select)

        self.widget.section_edit_pane.move_message_down_btn.click()
        list_item = self.widget.section_edit_pane.section_message_list.item(1)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['messages'][1], message)
        self.assertEqual(list_item.text(), message)

    def test_add_choice_with_message_solution_to_section(self):
        self.assertEqual(self.widget.section_edit_pane.section_choice_list.rowCount(), 0)
        choice = 'Yes'
        message = 'Clear all settings'
        solution_type = self.helper_create_message_choice(choice, message)
        self.assertEqual(self.widget.section_edit_pane.section_choice_list.rowCount(), 1)
        self.assertEqual(len(self.model.get_section_by_id(self.section_id)['choices']), 1)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['choices'][0], choice)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['solution_type'][0], solution_type)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['solution_message'][0], message)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['solution_section_id'][0], None)

    def test_move_choice_up(self):
        choice_1 = 'Yes'
        message_1 = 'Clear all settings'
        self.helper_create_message_choice(choice_1, message_1)

        choice_2 = 'No'
        next_section_id_2 = 'section_b'
        self.helper_create_section_choice(choice_2, next_section_id_2)

        list_item = self.widget.section_edit_pane.section_choice_list.item(1, 0)
        self.widget.section_edit_pane.section_choice_list.setCurrentItem(
            list_item, QtCore.QItemSelectionModel.Select)

        self.widget.section_edit_pane.move_choice_up_btn.click()
        list_item = self.widget.section_edit_pane.section_choice_list.item(0, 0)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['choices'][0], choice_2)
        self.assertEqual(list_item.text(), choice_2)

    def test_move_choice_down(self):
        sys.excepthook = excepthook
        choice_1 = 'Yes'
        message_1 = 'Clear all settings'
        self.helper_create_message_choice(choice_1, message_1)

        choice_2 = 'No'
        next_section_id_2 = 'section_b'
        self.helper_create_section_choice(choice_2, next_section_id_2)

        list_item = self.widget.section_edit_pane.section_choice_list.item(0, 0)
        self.widget.section_edit_pane.section_choice_list.setCurrentItem(
            list_item, QtCore.QItemSelectionModel.Select)

        self.widget.section_edit_pane.move_choice_down_btn.click()
        list_item = self.widget.section_edit_pane.section_choice_list.item(1, 0)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['choices'][1], choice_1)
        self.assertEqual(list_item.text(), choice_1)

    def test_add_choice_with_section_solution_to_section(self):
        self.assertEqual(self.widget.section_edit_pane.section_choice_list.rowCount(), 0)
        choice = 'No'
        next_section_id = 'section_b'
        solution_type = self.helper_create_section_choice(choice, next_section_id)
        self.assertEqual(self.widget.section_edit_pane.section_choice_list.rowCount(), 1)
        self.assertEqual(len(self.model.get_section_by_id(self.section_id)['choices']), 1)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['choices'][0], choice)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['solution_type'][0], solution_type)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['solution_message'][0], SECTION_SOLUTION)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['solution_section_id'][0], next_section_id)

    def test_remove_choice_from_section_when_row_selected(self):
        choice = 'Yes'
        message = 'Clear all settings'
        self.helper_create_message_choice(choice, message)
        self.assertEqual(self.widget.section_edit_pane.section_choice_list.rowCount(), 1)
        self.widget.section_edit_pane.section_choice_list.selectRow(0)
        self.widget.section_edit_pane.remove_choice_btn.click()
        self.assertEqual(self.widget.section_edit_pane.section_choice_list.rowCount(), 0)
        self.assertEqual(len(self.model.get_section_by_id(self.section_id)['choices']), 0)

    def test_remove_choice_from_section_when_item_selected(self):
        choice = 'Yes'
        message = 'Clear all settings'
        self.helper_create_message_choice(choice, message)
        self.assertEqual(self.widget.section_edit_pane.section_choice_list.rowCount(), 1)
        list_item = self.widget.section_edit_pane.section_choice_list.item(0, 0)
        self.widget.section_edit_pane.section_choice_list.setCurrentItem(
            list_item, QtCore.QItemSelectionModel.Select)

        self.widget.section_edit_pane.remove_choice_btn.click()

        self.assertEqual(self.widget.section_edit_pane.section_choice_list.rowCount(), 0)
        self.assertEqual(len(self.model.get_section_by_id(self.section_id)['choices']), 0)

    def test_edit_choice_with_message_solution(self):
        choice = 'Yes'
        message = 'Clear all settings'

        solution_type = self.helper_create_message_choice(choice, message)

        self.assertEqual(self.model.get_section_by_id(self.section_id)['choices'][0], choice)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['solution_type'][0], solution_type)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['solution_message'][0], message)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['solution_section_id'][0], None)

        list_item = self.widget.section_edit_pane.section_choice_list.item(0, 0)
        self.widget.section_edit_pane.section_choice_list.setCurrentItem(
            list_item, QtCore.QItemSelectionModel.Select)

        new_choice = 'Maybe'
        new_message = 'Do Nothing'
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[new_choice, True], [new_message, True]])
        self.widget.section_edit_pane.section_choice_list.itemDoubleClicked.emit(
            list_item)
        list_item = self.widget.section_edit_pane.section_choice_list.item(0, 0)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['choices'][0], new_choice)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['solution_message'][0], new_message)
        self.assertEqual(list_item.text(), new_choice)

    def test_edit_choice_with_section_solution(self):
        # sys.excepthook = excepthook
        choice = 'No'
        next_section_id = 'section_b'
        solution_type = self.helper_create_section_choice(choice, next_section_id)
        self.assertEqual(self.widget.section_edit_pane.section_choice_list.rowCount(), 1)
        self.assertEqual(len(self.model.get_section_by_id(self.section_id)['choices']), 1)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['choices'][0], choice)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['solution_type'][0], solution_type)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['solution_message'][0], SECTION_SOLUTION)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['solution_section_id'][0], next_section_id)

        list_item = self.widget.section_edit_pane.section_choice_list.item(0, 0)
        self.widget.section_edit_pane.section_choice_list.setCurrentItem(
            list_item, QtCore.QItemSelectionModel.Select)

        new_choice = 'Maybe'
        new_next_section_id = 'section_c'
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[new_choice, True]])
        QtWidgets.QInputDialog.getItem = MagicMock(side_effect=[[new_next_section_id, True]])

        self.widget.section_edit_pane.section_choice_list.itemDoubleClicked.emit(
            list_item)
        list_item = self.widget.section_edit_pane.section_choice_list.item(0, 0)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['choices'][0], new_choice)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['solution_message'][0], SECTION_SOLUTION)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['solution_section_id'][0], new_next_section_id)
        self.assertEqual(list_item.text(), new_choice)

    def test_only_new_section_appears_empty(self):
        message = 'message_1'
        self.helper_create_text_message(message)
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 1)

        choice = 'Yes'
        message = 'Clear all settings'
        self.helper_create_message_choice(choice, message)
        self.assertEqual(self.widget.section_edit_pane.section_choice_list.rowCount(), 1)

        self.section_id_b = 'section_b'
        self.controller.section_id = self.section_id_b
        self.widget.set_selected_category(self.cat_id)
        self.widget.add_section_btn.click()

        self.assertEqual(self.model.section_counter(self.cat_id), 2)
        self.widget.set_selected_section(self.section_id_b)
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 0)
        self.assertEqual(self.widget.section_edit_pane.section_choice_list.rowCount(), 0)

        self.widget.set_selected_section(self.section_id)
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 1)
        self.assertEqual(self.widget.section_edit_pane.section_choice_list.rowCount(), 1)

    def helper_is_widget_in_layout(self, widget, layout):
        for ind in range(layout.count()):
            item = layout.itemAt(ind)
            if item.widget() == widget:
                return True
        return False

    def helper_create_text_message(self, message):
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=['Text', True])
        QtWidgets.QInputDialog.getText = MagicMock(return_value=[message, True])
        self.widget.section_edit_pane.add_message_btn.click()

    def helper_create_image_message(self, image_filename):
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=['Image', True])
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=[image_filename, ''])
        self.widget.section_edit_pane.add_message_btn.click()

    def helper_create_pv_message(self, message, pv):
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=['PV_string', True])
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[message, True], [pv, True]])
        epics.caget = MagicMock(return_value=37077)

        self.widget.section_edit_pane.add_message_btn.click()

    def helper_create_message_choice(self, choice, message):
        solution_type = 'message'
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[choice, True], [message, True]])
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=[solution_type, True])
        self.widget.section_edit_pane.add_choice_btn.click()
        return solution_type

    def helper_create_section_choice(self, choice, next_section_id):
        solution_type = 'section'
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[choice, True]])
        QtWidgets.QInputDialog.getItem = MagicMock(side_effect=[[solution_type, True], [next_section_id, True]])
        self.widget.section_edit_pane.add_choice_btn.click()
        return solution_type
