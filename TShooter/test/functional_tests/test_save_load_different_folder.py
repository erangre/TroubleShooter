import os, sys
from shutil import copyfile, rmtree
import gc

# import numpy as np
from qtpy import QtWidgets, QtCore, QtGui
# from qtpy.QtTest import QTest
from mock import MagicMock
try:
    import epics
    ep = True
except ModuleNotFoundError:
    from ...controller.utils import FakeEpics
    epics = FakeEpics()
    ep = False
from ..utility import QtTest, click_button

import time

from ...controller.MainController import MainController
from ...model.tshoot_model import TroubleShooter, SECTION_SOLUTION
from ...widget.MainWidget import MainWidget
from ..utility import excepthook

unittest_path = os.path.dirname(__file__)
data_path = os.path.join(unittest_path, '../data')


class SaveLoadInDifferentFolders(QtTest):
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
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[self.cat_id, True], [caption, True]])
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=[image, ''])
        self.widget.add_category_btn.click()

        self.section_id = 'section_a'
        self.controller.section_id = self.section_id
        self.widget.add_section_btn.click()

    def tearDown(self):
        del self.controller
        gc.collect()

    def test_loading_image_in_different_folder(self):
        # sys.excepthook = excepthook

        original_image_filename = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        first_dir = os.path.normpath(os.path.join(data_path, "first"))
        second_dir = os.path.normpath(os.path.join(data_path, "second"))
        os.makedirs(os.path.join(first_dir, 'images'), exist_ok=True)
        os.makedirs(os.path.join(second_dir, 'images'), exist_ok=True)
        image_filename = os.path.normpath(os.path.join(first_dir, "images/beam_status.png"))
        new_image_filename = os.path.normpath(os.path.join(second_dir, "images/beam_status.png"))
        copyfile(original_image_filename, image_filename)
        copyfile(original_image_filename, new_image_filename)

        self.helper_create_image_message(image_filename)

        save_filename = os.path.normpath(os.path.join(first_dir, 'tshooter_temp2.yml'))
        QtWidgets.QFileDialog.getSaveFileName = MagicMock(return_value=(save_filename, True))
        self.widget.save_tshooter_btn.click()

        load_filename = os.path.normpath(os.path.join(second_dir, 'tshooter_temp2.yml'))
        copyfile(save_filename, load_filename)

        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=(load_filename, True))
        QtWidgets.QMessageBox.exec_ = MagicMock(return_value=QtWidgets.QMessageBox.Ok)
        self.widget.load_tshooter_btn.click()

        self.assertEqual(len(self.model.get_section_by_id(self.section_id)['messages']), 1)
        self.assertEqual(self.model.get_section_by_id(self.section_id)['messages'][0], new_image_filename)
        self.widget.set_selected_section(self.section_id)
        self.assertEqual(self.widget.section_edit_pane.section_message_list.count(), 1)
        self.assertEqual(self.widget.section_edit_pane.section_message_list.item(0).text(), new_image_filename)

        rmtree(first_dir)
        rmtree(second_dir)

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
        if ep:
            epics.caget = MagicMock(return_value='37077')
        else:
            FakeEpics.caget = MagicMock(return_value='37077')

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
