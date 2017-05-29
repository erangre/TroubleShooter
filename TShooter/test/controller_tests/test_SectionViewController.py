import os, sys
import gc

# import numpy as np
from qtpy import QtWidgets, QtCore, QtGui
# from qtpy.QtTest import QTest
from mock import MagicMock
from ..utility import QtTest, click_button

from ...controller.MainController import MainController
from ...model.tshoot_model import TroubleShooter, SECTION_SOLUTION
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

        self.message_1 = 'message_1'  # add a text message
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=['Text', True])
        QtWidgets.QInputDialog.getText = MagicMock(return_value=[self.message_1, True])
        self.widget.section_edit_pane.add_message_btn.click()

        self.image_filename = os.path.join(data_path, "images/beam_status.png")  # add an image message
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=['Image', True])
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=[self.image_filename, ''])
        self.widget.section_edit_pane.add_message_btn.click()

        self.choice_1 = 'Yes'  # add a choice with text solution
        self.message_choice_1 = 'Clear all settings'
        solution_type = 'message'
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[self.choice_1, True], [self.message_choice_1, True]])
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=[solution_type, True])
        self.widget.section_edit_pane.add_choice_btn.click()

        self.choice_2 = 'No'  # add a choice with a section solution
        solution_type = 'section'
        self.next_section_id = 'section_b'
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[self.choice_2, True]])
        QtWidgets.QInputDialog.getItem = MagicMock(side_effect=[[solution_type, True], [self.next_section_id, True]])
        self.widget.section_edit_pane.add_choice_btn.click()

        self.section_id_b = 'section_b'
        self.controller.section_id = self.section_id_b
        self.widget.add_section_btn.click()

        self.widget.set_selected_category(self.cat_id)  # go to a category and back to update before testing
        self.widget.set_selected_section(self.section_id)

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

    def test_selecting_section_updates_section_view_caption_and_id(self):
        current_section = self.model.get_section_by_id(self.section_id)
        section_caption = current_section['caption']
        self.assertEqual(self.widget.section_view_pane.section_caption_lbl.text(), section_caption)
        self.assertEqual(self.widget.section_view_pane.section_id_lbl.text(), self.section_id)

    def test_selecting_section_updates_section_view_messages(self):
        messages = []

        for msg in self.widget.section_view_pane.messages:
            messages.append(msg.text())
        self.assertIn(self.message_1, messages)
        self.assertIn(self.image_filename, messages)

    def test_selecting_section_updates_section_view_choices(self):
        choices = []

        for choice in self.widget.section_view_pane.choices:
            choices.append(choice.text())
        self.assertIn(self.choice_1, choices)
        self.assertIn(self.choice_2, choices)

    def test_clicking_on_choice_button_reveals_solution(self):
        self.assertFalse(self.widget.section_view_pane.next_section_btn.isEnabled())
        current_section = self.model.get_section_by_id(self.section_id)

        for ind in range(0, len(self.widget.section_view_pane.choices)):
            choice_btn = self.widget.section_view_pane.choices[ind]
            choice_btn.click()
            if current_section['solution_type'][ind] == 'message':
                self.assertEqual(self.widget.section_view_pane.solution_message_lbl.text(),
                                 current_section['solution_message'][ind])
            elif current_section['solution_type'][ind] == 'section':
                self.assertEqual(self.widget.section_view_pane.solution_message_lbl.text(),
                                 SECTION_SOLUTION)
                self.assertTrue(self.widget.section_view_pane.next_section_btn.isEnabled())
                self.widget.section_view_pane.next_section_btn.click()
                self.assertEqual(self.widget.section_view_pane.section_id_lbl.text(),
                                 current_section['solution_section_id'][ind])
                self.assertTrue(self.widget.section_view_pane.previous_section_btn.isEnabled())
                self.widget.section_view_pane.previous_section_btn.click()
                self.assertEqual(self.widget.section_view_pane.section_id_lbl.text(),
                                 self.section_id)

    def helper_is_widget_in_layout(self, widget, layout):
        for ind in range(layout.count()):
            item = layout.itemAt(ind)
            if item.widget() == widget:
                return True
        return False
