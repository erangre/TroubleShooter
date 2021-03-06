import os, sys
import gc

# import numpy as np
from qtpy import QtWidgets, QtCore
# from qtpy.QtTest import QTest
from mock import MagicMock
from ..utility import QtTest, click_button

from ...controller.MainController import MainController
from ...model.tshoot_model import TroubleShooter
from ...widget.MainWidget import MainWidget
from ..utility import excepthook

unittest_path = os.path.dirname(__file__)
data_path = os.path.join(unittest_path, '../data')


class CategoryTests(QtTest):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance()
        if cls.app is None:
            cls.app = QtWidgets.QApplication([])

    def setUp(self):
        self.controller = MainController()
        self.model = self.controller.model  # type: TroubleShooter
        # sys.excepthook = excepthook

    def tearDown(self):
        del self.controller
        gc.collect()

    def test_add_category(self):
        self.assertEqual(self.controller.widget.main_tree.currentItem(), self.controller.widget.categories["main"])
        cat_id = 'test_subcategory'
        caption = 'caption_test'
        image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        parent_id = 'main'
        level = 1

        self.helper_create_category(cat_id, caption, image)

        self.assertEqual(self.controller.widget.main_tree.currentItem(), self.controller.widget.categories[cat_id])
        self.assertIsNotNone(self.controller.widget.categories.get(cat_id, None))
        self.assertEqual(self.controller.widget.categories.get(cat_id, None).text(0), caption)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['caption'], caption)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['level'], level)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['parent_id'], parent_id)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['image'], image)

    def test_add_subcategory(self):
        cat_id = 'test_subcategory'
        caption = 'caption_test'
        image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        parent_id = 'main'
        cat_level = 1
        self.helper_create_category(cat_id, caption, image)

        subcat_id = 'test_sub_cat'
        subcat_caption = 'sub cat!'
        subcat_parent_id = cat_id
        subcat_level = 2
        subcat_image = os.path.normpath(os.path.join(data_path, "images/garfield.png"))

        self.helper_create_category(subcat_id, subcat_caption, subcat_image)

        self.assertEqual(self.controller.widget.main_tree.currentItem(), self.controller.widget.categories[subcat_id])
        added_sub_category = self.controller.model.get_category_by_id(subcat_id)
        self.assertEqual(added_sub_category['level'], subcat_level)
        self.assertEqual(added_sub_category['parent_id'], cat_id)

        # TODO - add category id in tree_widget column

    def test_add_two_categories(self):
        cat_id = 'test_subcategory'
        caption = 'caption_test'
        image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))

        self.helper_create_category(cat_id, caption, image)

        # simulate the user choosing the main category again
        self.controller.widget.set_selected_category("main")

        cat_id = 'test_subcategory2'
        caption = 'caption_test2'
        image = os.path.normpath(os.path.join(data_path, "images/garfield.png"))
        parent_id = 'main'
        level = 1

        self.helper_create_category(cat_id, caption, image)

        self.assertEqual(self.controller.widget.main_tree.currentItem(), self.controller.widget.categories[cat_id])

        self.assertIsNotNone(self.controller.widget.categories.get(cat_id, None))
        self.assertEqual(self.controller.widget.categories.get(cat_id, None).text(0), caption)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['caption'], caption)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['level'], level)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['parent_id'], parent_id)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['image'], image)

    def test_remove_category(self):
        cat_id = 'test_subcategory'
        caption = 'caption_test'
        image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        parent_id = 'main'
        cat_level = 1

        self.helper_create_category(cat_id, caption, image)

        tree_widget_item = self.controller.widget.categories[cat_id]
        self.assertEqual(self.controller.widget.main_tree.currentItem(), tree_widget_item)
        QtWidgets.QMessageBox.exec_ = MagicMock(return_value=QtWidgets.QMessageBox.Ok)
        self.controller.widget.remove_category_btn.click()
        self.assertNotEqual(self.controller.widget.main_tree.currentItem(), tree_widget_item)

    def test_cannot_add_same_category_twice(self):
        cat_id = 'test_subcategory'
        caption = 'caption_test'
        image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        parent_id = 'main'
        level = 1

        self.helper_create_category(cat_id, caption, image)
        self.assertEqual(self.controller.model.subcategory_counter("main"), 1)
        self.helper_create_category(cat_id, caption, image)
        self.assertEqual(self.controller.model.subcategory_counter("main"), 1)

    def test_edit_category(self):
        cat_id = 'test_subcategory'
        caption = 'caption_test'
        image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        parent_id = 'main'
        level = 1
        self.helper_create_category(cat_id, caption, image)
        new_caption = 'caption_changed'
        new_image = os.path.normpath(os.path.join(data_path, "images/garfield.png"))
        QtWidgets.QInputDialog.getText = MagicMock(return_value=[new_caption, True])
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=[new_image, ''])
        self.controller.widget.edit_category_btn.click()
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['caption'], new_caption)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['level'], level)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['parent_id'], parent_id)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['image'], new_image)
        self.assertEqual(self.controller.widget.categories.get(cat_id, None).text(0), new_caption)

    def test_move_category_up(self):
        # sys.excepthook = excepthook
        image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        parent_id = 'main'
        cat_id_a = 'cat_a'
        caption_a = 'cat a'
        cat_id_b = 'cat_b'
        caption_b = 'cat b'
        self.helper_create_category(cat_id_a, caption_a, image)
        self.controller.widget.set_selected_category("main")
        self.helper_create_category(cat_id_b, caption_b, image)

        self.controller.widget.set_selected_category(cat_id_b)

        # First check the model before the move:
        cat_subcats = list(self.model.get_category_by_id(parent_id)['subcategories'].items())
        self.assertEqual(cat_subcats[1][0], cat_id_b)
        self.assertEqual(cat_subcats[1][1]['id'], cat_id_b)

        old_index = self.controller.widget.main_tree.indexFromItem(
            self.controller.widget.main_tree.selectedItems()[0]).row()

        self.controller.widget.move_tree_item_up_btn.click()
        self.controller.widget.set_selected_category(cat_id_b)

        new_index = self.controller.widget.main_tree.indexFromItem(
            self.controller.widget.main_tree.selectedItems()[0]).row()

        self.assertEqual(old_index - 1, new_index)

        # Then check the model after the move:
        cat_subcats = list(self.model.get_category_by_id(parent_id)['subcategories'].items())
        self.assertEqual(cat_subcats[0][0], cat_id_b)
        self.assertEqual(cat_subcats[0][1]['id'], cat_id_b)

    def test_move_category_down(self):
        # sys.excepthook = excepthook
        image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        parent_id = 'main'
        cat_id_a = 'cat_a'
        caption_a = 'cat a'
        cat_id_b = 'cat_b'
        caption_b = 'cat b'
        self.helper_create_category(cat_id_a, caption_a, image)
        self.controller.widget.set_selected_category("main")
        self.helper_create_category(cat_id_b, caption_b, image)

        self.controller.widget.set_selected_category(cat_id_a)

        # First check the model before the move:
        cat_subcats = list(self.model.get_category_by_id(parent_id)['subcategories'].items())
        self.assertEqual(cat_subcats[0][0], cat_id_a)
        self.assertEqual(cat_subcats[0][1]['id'], cat_id_a)

        old_index = self.controller.widget.main_tree.indexFromItem(
            self.controller.widget.main_tree.selectedItems()[0]).row()

        self.controller.widget.move_tree_item_down_btn.click()
        self.controller.widget.set_selected_category(cat_id_a)

        new_index = self.controller.widget.main_tree.indexFromItem(
            self.controller.widget.main_tree.selectedItems()[0]).row()

        self.assertEqual(old_index + 1, new_index)

        # Then check the model after the move:
        cat_subcats = list(self.model.get_category_by_id(parent_id)['subcategories'].items())
        self.assertEqual(cat_subcats[1][0], cat_id_a)
        self.assertEqual(cat_subcats[1][1]['id'], cat_id_a)

    def test_move_subcategory_up(self):
        # sys.excepthook = excepthook
        image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        parent_id = 'cat_a'
        cat_id_a = 'cat_a'
        caption_a = 'cat a'
        cat_id_b = 'cat_b'
        caption_b = 'cat b'
        cat_id_c = 'cat_c'
        caption_c = 'cat c'
        self.helper_create_category(cat_id_a, caption_a, image)
        self.helper_create_category(cat_id_b, caption_b, image)
        self.controller.widget.set_selected_category("cat_a")
        self.helper_create_category(cat_id_c, caption_c, image)

        self.controller.widget.set_selected_category(cat_id_c)

        # First check the model before the move:
        cat_subcats = list(self.model.get_category_by_id(parent_id)['subcategories'].items())
        self.assertEqual(cat_subcats[1][0], cat_id_c)
        self.assertEqual(cat_subcats[1][1]['id'], cat_id_c)

        old_index = self.controller.widget.main_tree.indexFromItem(
            self.controller.widget.main_tree.selectedItems()[0]).row()

        self.controller.widget.move_tree_item_up_btn.click()
        self.controller.widget.set_selected_category(cat_id_c)

        new_index = self.controller.widget.main_tree.indexFromItem(
            self.controller.widget.main_tree.selectedItems()[0]).row()

        self.assertEqual(old_index - 1, new_index)

        # Then check the model after the move:
        cat_subcats = list(self.model.get_category_by_id(parent_id)['subcategories'].items())
        self.assertEqual(cat_subcats[0][0], cat_id_c)
        self.assertEqual(cat_subcats[0][1]['id'], cat_id_c)

    def helper_create_category(self, cat_id, caption, image):
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[cat_id, True], [caption, True]])
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=[image, ''])
        self.controller.widget.add_category_btn.click()


class SectionTests(QtTest):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance()
        if cls.app is None:
            cls.app = QtWidgets.QApplication([])

    def setUp(self):
        self.controller = MainController()
        self.model = self.controller.model  # type: TroubleShooter
        self.cat_id = 'first_category'
        caption = 'The first category!'
        image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))

        self.helper_create_category(self.cat_id, caption, image)

    def tearDown(self):
        del self.controller
        gc.collect()

    def test_add_section_to_category(self):
        section_id = 'section_a'
        parent_id = self.cat_id
        level = 2
        self.helper_create_section(section_id)

        self.assertEqual(self.controller.widget.main_tree.currentItem(), self.controller.widget.sections[section_id])
        self.assertEqual(self.controller.model.get_section_by_id(section_id)['parent_id'], parent_id)
        self.assertEqual(self.controller.model.get_section_by_id(section_id)['level'], level)

    def test_add_two_sections_to_one_category(self):
        # add first section
        section_id_a = 'section_a'
        self.helper_create_section(section_id_a)
        self.assertEqual(self.controller.widget.main_tree.currentItem(), self.controller.widget.sections[section_id_a])

        # simulate the user choosing the category again
        self.controller.widget.set_selected_category(self.cat_id)

        # add 2nd section
        section_id_b = 'section_b'
        parent_id = self.cat_id
        level = 2
        self.helper_create_section(section_id_b)

        self.assertEqual(self.controller.widget.main_tree.currentItem(), self.controller.widget.sections[section_id_b])
        self.assertEqual(self.controller.model.get_section_by_id(section_id_a)['parent_id'], parent_id)
        self.assertEqual(self.controller.model.get_section_by_id(section_id_b)['parent_id'], parent_id)
        self.assertEqual(self.controller.model.get_section_by_id(section_id_a)['level'], level)

    def test_cannot_add_section_to_main_category(self):
        sections_widget = self.controller.widget.sections
        self.controller.widget.set_selected_category("main")
        section_id = 'section_a'
        self.helper_create_section(section_id)
        self.assertDictEqual(self.controller.widget.sections, sections_widget)
        self.assertIsNone(self.controller.model.get_section_by_id(section_id))

    def test_cannot_add_section_to_category_with_sub_categories(self):
        subcat_id = 'test_sub_cat'
        subcat_caption = 'sub cat!'
        image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))

        self.helper_create_category(subcat_id, subcat_caption, image)

        self.controller.widget.set_selected_category(self.cat_id)
        section_id = 'section_a'
        self.helper_create_section(section_id)
        self.assertIsNone(self.controller.model.get_section_by_id(section_id))

    def test_cannot_add_subcategory_to_category_with_sections(self):
        section_id = 'section_a'
        self.controller.section_id = section_id
        self.controller.widget.add_section_btn.click()

        self.controller.widget.set_selected_category(self.cat_id)

        subcat_id = 'test_sub_cat'
        subcat_caption = 'sub cat!'
        image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))

        self.helper_create_category(subcat_id, subcat_caption, image)
        self.assertIsNone(self.controller.model.get_category_by_id(subcat_id))

    def test_cannot_add_subcategory_in_section(self):
        section_id = 'section_a'
        self.helper_create_section(section_id)

        subcat_id = 'test_sub_cat'
        subcat_caption = 'sub cat!'
        image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))

        self.helper_create_category(subcat_id, subcat_caption, image)

        self.assertIsNone(self.controller.model.get_category_by_id(subcat_id))

    def test_adding_section_when_section_selected_adds_section_to_parent_category(self):
        section_id = 'section_a'
        self.helper_create_section(section_id)
        self.assertEqual(self.controller.model.section_counter(self.cat_id), 1)

        section_id = 'section_b'
        self.helper_create_section(section_id)
        self.assertEqual(self.controller.model.section_counter(self.cat_id), 2)

    def test_cannot_add_section_with_existing_name(self):
        section_id = 'section_a'
        self.helper_create_section(section_id)
        self.assertEqual(self.controller.model.section_counter(self.cat_id), 1)

        section_id = 'section_a'
        self.helper_create_section(section_id)
        self.assertEqual(self.controller.model.section_counter(self.cat_id), 1)
        # Note: This test doesn't actually make sure that you cannot add with an existing name.
        # This is because it might be adding the same one again and the model doesn't change but the widget has two of
        # the same section.

    def test_edit_section(self):
        # sys.excepthook = excepthook
        section_id = 'section_a'
        parent_id = self.cat_id
        self.helper_create_section(section_id)
        self.controller.widget.set_selected_section(section_id)
        new_section_id = 'section_x'
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[new_section_id, True]])
        self.controller.widget.edit_category_btn.click()
        self.controller.widget.set_selected_section(new_section_id)

        self.assertEqual(self.controller.widget.get_selected_categories()[0].text(0), new_section_id)
        self.assertFalse(section_id in self.controller.model.get_category_by_id(parent_id)['sections'])
        self.assertTrue(new_section_id in self.controller.model.get_category_by_id(parent_id)['sections'])

    def test_move_section_up(self):
        section_id_a = 'section_a'
        parent_id = self.cat_id
        self.helper_create_section(section_id_a)

        section_id_b = 'section_b'
        parent_id = self.cat_id
        self.helper_create_section(section_id_b)

        # First check the model before the move:
        cat_sections = list(self.model.get_category_by_id(parent_id)['sections'].items())
        self.assertEqual(cat_sections[1][0], section_id_b)
        self.assertEqual(cat_sections[1][1]['id'], section_id_b)

        self.controller.widget.set_selected_section(section_id_b)
        old_index = self.controller.widget.main_tree.indexFromItem(
            self.controller.widget.main_tree.selectedItems()[0]).row()

        self.controller.widget.move_tree_item_up_btn.click()

        self.controller.widget.set_selected_section(section_id_b)
        new_index = self.controller.widget.main_tree.indexFromItem(
            self.controller.widget.main_tree.selectedItems()[0]).row()
        self.assertEqual(old_index - 1, new_index)

        # Now check the model after the move:
        cat_sections = list(self.model.get_category_by_id(parent_id)['sections'].items())
        self.assertEqual(cat_sections[0][0], section_id_b)
        self.assertEqual(cat_sections[0][1]['id'], section_id_b)

    def test_move_section_down(self):
        section_id_a = 'section_a'
        parent_id = self.cat_id
        self.helper_create_section(section_id_a)

        section_id_b = 'section_b'
        parent_id = self.cat_id
        self.helper_create_section(section_id_b)

        # First check the model before the move:
        cat_sections = list(self.model.get_category_by_id(parent_id)['sections'].items())
        self.assertEqual(cat_sections[0][0], section_id_a)
        self.assertEqual(cat_sections[0][1]['id'], section_id_a)

        self.controller.widget.set_selected_section(section_id_a)
        old_index = self.controller.widget.main_tree.indexFromItem(
            self.controller.widget.main_tree.selectedItems()[0]).row()

        self.controller.widget.move_tree_item_down_btn.click()

        self.controller.widget.set_selected_section(section_id_a)
        new_index = self.controller.widget.main_tree.indexFromItem(
            self.controller.widget.main_tree.selectedItems()[0]).row()
        self.assertEqual(old_index + 1, new_index)

        # Now check the model after the move:
        cat_sections = list(self.model.get_category_by_id(parent_id)['sections'].items())
        self.assertEqual(cat_sections[1][0], section_id_a)
        self.assertEqual(cat_sections[1][1]['id'], section_id_a)

    def helper_create_category(self, cat_id, caption, image):
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[cat_id, True], [caption, True]])
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=[image, ''])
        self.controller.widget.add_category_btn.click()

    def helper_create_section(self, section_id):
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[section_id, True]])
        self.controller.widget.add_section_btn.click()


class SaveLoadTests(QtTest):
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
        self.helper_create_category(self.cat_id, caption, image)

        self.section_id = 'section_a'
        self.helper_create_section(self.section_id)

        self.message_1 = 'message_1'  # add a text message
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=['Text', True])
        QtWidgets.QInputDialog.getText = MagicMock(return_value=[self.message_1, True])
        self.widget.section_edit_pane.add_message_btn.click()

        self.image_filename = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))  # add an image message
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
        self.helper_create_section(self.section_id_b)

        self.widget.set_selected_category(self.cat_id)  # go to a category and back to update before testing
        self.widget.set_selected_section(self.section_id)

        self.widget.set_selected_category('main')

        self.cat_id2 = 'second_category'
        caption = 'The second category!'
        image = os.path.normpath(os.path.join(data_path, "images/garfield.png"))
        self.helper_create_category(self.cat_id2, caption, image)

        self.section_id_c = 'section_c'
        self.helper_create_section(self.section_id_c)

        self.message_c1 = 'message_c1'  # add a text message
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=['Text', True])
        QtWidgets.QInputDialog.getText = MagicMock(return_value=[self.message_c1, True])
        self.widget.section_edit_pane.add_message_btn.click()

        self.choice_c1 = 'Yes'  # add a choice with text solution
        self.message_choice_c1 = 'Clear all settings'
        solution_type = 'message'
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[self.choice_c1, True], [self.message_choice_c1, True]])
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=[solution_type, True])
        self.widget.section_edit_pane.add_choice_btn.click()

        self.n_categories_in_main = self.model.subcategory_counter('main')

    def tearDown(self):
        del self.controller
        gc.collect()

    def test_save_button_creates_file(self):
        filename = os.path.normpath(os.path.join(data_path, 'tshooter_temp1.yml'))
        QtWidgets.QFileDialog.getSaveFileName = MagicMock(return_value=(filename, True))
        self.widget.save_tshooter_btn.click()
        self.assertTrue(os.path.isfile(filename))

    def test_clear_button_clears_everything(self):
        QtWidgets.QMessageBox.exec_ = MagicMock(return_value=QtWidgets.QMessageBox.Ok)
        self.widget.clear_tshooter_btn.click()
        self.assertEqual(self.model.subcategory_counter('main'), 0)
        self.assertEqual(self.model.all_section_counter(), 0)
        self.assertEqual(len(self.widget.categories), 1)  # main category should still exist
        self.assertEqual(len(self.widget.sections), 0)

    def test_clear_and_cancel_does_not_clear(self):
        QtWidgets.QMessageBox.exec_ = MagicMock(return_value=QtWidgets.QMessageBox.Cancel)
        self.widget.clear_tshooter_btn.click()
        self.assertNotEqual(self.model.subcategory_counter('main'), 0)

    def test_load_button_fills_tree(self):
        # sys.excepthook = excepthook
        filename = os.path.normpath(os.path.join(data_path, 'tshooter_temp1.yml'))
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=(filename, True))
        QtWidgets.QMessageBox.exec_ = MagicMock(return_value=QtWidgets.QMessageBox.Ok)
        self.widget.load_tshooter_btn.click()
        self.assertEqual(self.model.subcategory_counter('main'), 2)
        self.assertEqual(self.model.section_counter('first_category'), 2)
        self.assertEqual(self.model.section_counter('second_category'), 1)

        # test if exists in widget
        self.assertEqual(len(self.widget.categories), 3)
        self.assertEqual(len(self.widget.sections), 3)

    def test_clear_with_subcats(self):
        # sys.excepthook = excepthook
        filename = os.path.normpath(os.path.join(data_path, 'attempt1.yaml'))
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=(filename, True))
        QtWidgets.QMessageBox.exec_ = MagicMock(return_value=QtWidgets.QMessageBox.Ok)
        self.widget.load_tshooter_btn.click()
        self.widget.clear_tshooter_btn.click()

    def test_load_file_twice(self):
        # sys.excepthook = excepthook
        filename = os.path.normpath(os.path.join(data_path, 'attempt1.yaml'))
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=(filename, True))
        QtWidgets.QMessageBox.exec_ = MagicMock(return_value=QtWidgets.QMessageBox.Ok)
        self.widget.load_tshooter_btn.click()
        filename = os.path.normpath(os.path.join(data_path, 'attempt1.yaml'))
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=(filename, True))
        QtWidgets.QMessageBox.exec_ = MagicMock(return_value=QtWidgets.QMessageBox.Ok)
        self.widget.load_tshooter_btn.click()

    def test_load_in_view_mode_hides_edit_panels(self):
        self.helper_load_in_view_mode()

        self.assertFalse(self.helper_is_widget_in_layout(self.widget.section_edit_pane, self.widget._hlayout))
        self.assertFalse(self.helper_is_widget_in_layout(self.widget.edit_category_frame, self.widget._hlayout))
        self.assertTrue(self.helper_is_widget_in_layout(self.widget.view_category_frame, self.widget._hlayout))

    def test_load_in_view_mode_adds_buttons(self):
        self.helper_load_in_view_mode()
        self.assertEqual(len(self.widget._category_grid_btns), 2)
        self.assertEqual(self.widget._category_grid_btns[0].text(), "The first category!")
        self.assertEqual(self.widget._category_grid_btns[1].text(), "The second category!")

    def test_btns_in_view_mode_work(self):
        self.helper_load_in_view_mode()
        # check if clicking on a category button opens up what it has inside, in this case two section buttons
        self.widget._category_grid_btns[0].click()
        self.assertEqual(len(self.widget._category_grid_btns), 2)
        self.assertEqual(self.widget._category_grid_btns[0].text(), "section_a")
        self.assertEqual(self.widget._category_grid_btns[1].text(), "section_b")

        # check if clicking a section button shows the correct section in the view panel
        self.widget._category_grid_btns[0].click()
        self.assertEqual(self.widget.section_view_pane.message_layout.itemAt(0).widget().text(), 'message_1')

    def test_back_btn_in_view_mode(self):
        # sys.excepthook = excepthook
        self.helper_load_in_view_mode()
        self.widget._category_grid_btns[0].click()
        self.widget.category_view_back_btn.click()
        self.assertEqual(len(self.widget._category_grid_btns), 2)
        self.assertEqual(self.widget._category_grid_btns[0].text(), "The first category!")
        self.assertEqual(self.widget._category_grid_btns[1].text(), "The second category!")

    def helper_load_in_view_mode(self):
        filename = os.path.normpath(os.path.join(data_path, 'tshooter_temp1.yml'))
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=(filename, True))
        # Mock Ok to erase, No to edit
        QtWidgets.QMessageBox.exec_ = MagicMock(side_effect=[QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.No])
        self.widget.load_tshooter_btn.click()

    def helper_create_category(self, cat_id, caption, image):
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[cat_id, True], [caption, True]])
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=[image, ''])
        self.controller.widget.add_category_btn.click()

    def helper_is_widget_in_layout(self, widget_name, layout):
        """

        :param widget_name:
        :param layout:
        :type layout: QtWidgets.QLayout
        :return:
        """
        for ind in range(layout.count()):
            item = layout.itemAt(ind).widget()
            if widget_name == item:
                return True
        return False

    def helper_create_section(self, section_id):
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[section_id, True]])
        self.controller.widget.add_section_btn.click()


class SearchTests(QtTest):
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
        self.helper_create_category(self.cat_id, caption, image)

        self.section_id = 'section_a'
        self.helper_create_section(self.section_id)

        self.message_1 = 'message_1'  # add a text message
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=['Text', True])
        QtWidgets.QInputDialog.getText = MagicMock(return_value=[self.message_1, True])
        self.widget.section_edit_pane.add_message_btn.click()

        self.image_filename = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))  # add an image message
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
        self.helper_create_section(self.section_id_b)

        self.widget.set_selected_category(self.cat_id)  # go to a category and back to update before testing
        self.widget.set_selected_section(self.section_id)

        self.widget.set_selected_category('main')

        self.cat_id2 = 'second_category'
        caption = 'The second category!'
        image = os.path.normpath(os.path.join(data_path, "images/garfield.png"))
        self.helper_create_category(self.cat_id2, caption, image)

        self.section_id_c = 'section_c'
        self.helper_create_section(self.section_id_c)

        self.message_c1 = 'message_c1'  # add a text message
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=['Text', True])
        QtWidgets.QInputDialog.getText = MagicMock(return_value=[self.message_c1, True])
        self.widget.section_edit_pane.add_message_btn.click()

        self.choice_c1 = 'Yes'  # add a choice with text solution
        self.message_choice_c1 = 'Clear all settings'
        solution_type = 'message'
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[self.choice_c1, True], [self.message_choice_c1, True]])
        QtWidgets.QInputDialog.getItem = MagicMock(return_value=[solution_type, True])
        self.widget.section_edit_pane.add_choice_btn.click()

        self.helper_save_tshooter()
        self.helper_load_in_view_mode()

    def tearDown(self):
        del self.controller
        gc.collect()

    def test_search_changes_view(self):
        # sys.excepthook = excepthook
        self.widget.search_le.setText('age')
        self.assertFalse(self.helper_is_widget_in_layout(self.widget.section_edit_pane, self.widget._hlayout))
        self.assertFalse(self.helper_is_widget_in_layout(self.widget.edit_category_frame, self.widget._hlayout))
        self.assertFalse(self.helper_is_widget_in_layout(self.widget.view_category_frame, self.widget._hlayout))
        self.assertTrue(self.helper_is_widget_in_layout(self.widget.search_results_frame, self.widget._hlayout))

    def test_search_updates_search_table(self):
        # sys.excepthook = excepthook
        self.widget.search_le.setText('age')
        self.assertEqual(self.widget.search_results_table.rowCount(), 3)
        # make sure table clears to zero rows so that rows don't get added again when search term changes
        self.widget.search_le.setText('ag')
        self.assertEqual(self.widget.search_results_table.rowCount(), 3)

    def test_clicking_on_table_opens_correct_section(self):
        sys.excepthook = excepthook
        self.widget.search_le.setText('age')

        self.widget.search_results_table.cellClicked.emit(0, 1)
        self.assertEqual(self.widget.section_view_pane.message_layout.itemAt(0).widget().text(),
                         self.controller.highlight_msg('message_1', 'age'))
        self.widget.search_results_table.cellClicked.emit(0, 2)
        self.assertEqual(self.widget.section_view_pane.message_layout.itemAt(0).widget().text(),
                         self.controller.highlight_msg('message_1', 'age'))
        self.widget.search_results_table.cellClicked.emit(2, 1)
        self.assertEqual(self.widget.section_view_pane.message_layout.itemAt(0).widget().text(),
                         self.controller.highlight_msg('message_c1', 'age'))

    def helper_save_tshooter(self):
        filename = os.path.normpath(os.path.join(data_path, 'tshooter_temp1.yml'))
        QtWidgets.QFileDialog.getSaveFileName = MagicMock(return_value=(filename, True))
        self.widget.save_tshooter_btn.click()

    def helper_load_in_view_mode(self):
        filename = os.path.normpath(os.path.join(data_path, 'tshooter_temp1.yml'))
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=(filename, True))
        # Mock Ok to erase, No to edit
        QtWidgets.QMessageBox.exec_ = MagicMock(side_effect=[QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.No])
        self.widget.load_tshooter_btn.click()

    def helper_create_category(self, cat_id, caption, image):
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[cat_id, True], [caption, True]])
        QtWidgets.QFileDialog.getOpenFileName = MagicMock(return_value=[image, ''])
        self.controller.widget.add_category_btn.click()

    def helper_is_widget_in_layout(self, widget_name, layout):
        """

        :param widget_name:
        :param layout:
        :type layout: QtWidgets.QLayout
        :return:
        """
        for ind in range(layout.count()):
            item = layout.itemAt(ind).widget()
            if widget_name == item:
                return True
        return False

    def helper_create_section(self, section_id):
        QtWidgets.QInputDialog.getText = MagicMock(side_effect=[[section_id, True]])
        self.controller.widget.add_section_btn.click()
