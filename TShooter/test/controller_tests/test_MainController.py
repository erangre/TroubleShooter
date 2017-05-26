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
        # sys.excepthook = excepthook

    def tearDown(self):
        del self.controller
        gc.collect()

    def test_add_category(self):
        self.assertEqual(self.controller.widget._main_tree.currentItem(), self.controller.widget.categories["main"])
        cat_id = 'test_subcategory'
        caption = 'caption_test'
        image = os.path.join(data_path, "images/beam_status.png")
        parent_id = 'main'
        level = 1
        self.controller.category_info = {'id': cat_id,
                                         'caption': caption,
                                         'image': image,
                                         }
        self.controller.widget.add_category_btn.click()
        self.assertEqual(self.controller.widget._main_tree.currentItem(), self.controller.widget.categories[cat_id])
        self.assertIsNotNone(self.controller.widget.categories.get(cat_id, None))
        self.assertEqual(self.controller.widget.categories.get(cat_id, None).text(0), caption)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['caption'], caption)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['level'], level)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['parent_id'], parent_id)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['image'], image)

    def test_add_subcategory(self):
        cat_id = 'test_subcategory'
        caption = 'caption_test'
        image = os.path.join(data_path, "images/beam_status.png")
        parent_id = 'main'
        cat_level = 1

        self.controller.category_info = {'id': cat_id,
                                         'caption': caption,
                                         'image': image,
                                         }

        self.controller.widget.add_category_btn.click()

        subcat_id = 'test_sub_cat'
        subcat_caption = 'sub cat!'
        subcat_parent_id = cat_id
        subcat_level = 2

        self.controller.category_info = {'id': subcat_id,
                                         'caption': subcat_caption,
                                         'image': image,
                                         }
        self.controller.widget.add_category_btn.click()

        self.assertEqual(self.controller.widget._main_tree.currentItem(), self.controller.widget.categories[subcat_id])
        added_sub_category = self.controller.model.get_category_by_id(subcat_id)
        self.assertEqual(added_sub_category['level'], subcat_level)
        self.assertEqual(added_sub_category['parent_id'], cat_id)

    def test_add_two_categories(self):
        cat_id = 'test_subcategory'
        caption = 'caption_test'
        image = os.path.join(data_path, "images/beam_status.png")
        self.controller.category_info = {'id': cat_id,
                                         'caption': caption,
                                         'image': image,
                                         }
        self.controller.widget.add_category_btn.click()

        # simulate the user choosing the main category again
        self.controller.widget.set_selected_category("main")

        cat_id = 'test_subcategory2'
        caption = 'caption_test2'
        image = os.path.join(data_path, "images/beam_status.png")
        parent_id = 'main'
        level = 1
        self.controller.category_info = {'id': cat_id,
                                         'caption': caption,
                                         'image': image,
                                         }
        self.controller.widget.add_category_btn.click()

        self.assertEqual(self.controller.widget._main_tree.currentItem(), self.controller.widget.categories[cat_id])

        self.assertIsNotNone(self.controller.widget.categories.get(cat_id, None))
        self.assertEqual(self.controller.widget.categories.get(cat_id, None).text(0), caption)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['caption'], caption)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['level'], level)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['parent_id'], parent_id)
        self.assertEqual(self.controller.model.get_category_by_id(cat_id)['image'], image)


class SectionTests(QtTest):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance()
        if cls.app is None:
            cls.app = QtWidgets.QApplication([])

    def setUp(self):
        self.controller = MainController()
        self.cat_id = 'first_category'
        caption = 'The first category!'
        image = os.path.join(data_path, "images/beam_status.png")
        self.controller.category_info = {'id': self.cat_id,
                                         'caption': caption,
                                         'image': image,
                                         }
        self.controller.widget.add_category_btn.click()

    def tearDown(self):
        del self.controller
        gc.collect()

    def test_add_section_to_category(self):
        section_id = 'section_a'
        parent_id = self.cat_id
        level = 2
        self.controller.section_id = section_id
        self.controller.widget.add_section_btn.click()
        self.assertEqual(self.controller.widget._main_tree.currentItem(), self.controller.widget.sections[section_id])
        self.assertEqual(self.controller.model.get_section_by_id(section_id)['parent_id'], parent_id)
        self.assertEqual(self.controller.model.get_section_by_id(section_id)['level'], level)

    def test_add_two_sections_to_one_category(self):
        # add first section
        section_id_a = 'section_a'
        self.controller.section_id = section_id_a
        self.controller.widget.add_section_btn.click()
        self.assertEqual(self.controller.widget._main_tree.currentItem(), self.controller.widget.sections[section_id_a])

        # simulate the user choosing the category again
        self.controller.widget.set_selected_category(self.cat_id)

        # add 2nd section
        section_id_b = 'section_b'
        parent_id = self.cat_id
        level = 2
        self.controller.section_id = section_id_b
        self.controller.widget.add_section_btn.click()

        self.assertEqual(self.controller.widget._main_tree.currentItem(), self.controller.widget.sections[section_id_b])
        self.assertEqual(self.controller.model.get_section_by_id(section_id_a)['parent_id'], parent_id)
        self.assertEqual(self.controller.model.get_section_by_id(section_id_b)['parent_id'], parent_id)
        self.assertEqual(self.controller.model.get_section_by_id(section_id_a)['level'], level)

    def test_cannot_add_section_to_main_category(self):
        sections_widget = self.controller.widget.sections
        self.controller.widget.set_selected_category("main")
        section_id = 'section_a'
        self.controller.section_id = section_id
        self.controller.widget.add_section_btn.click()
        self.assertDictEqual(self.controller.widget.sections, sections_widget)
        self.assertIsNone(self.controller.model.get_section_by_id(section_id))

    def test_cannot_add_section_to_category_with_sub_categories(self):
        subcat_id = 'test_sub_cat'
        subcat_caption = 'sub cat!'
        image = os.path.join(data_path, "images/beam_status.png")

        self.controller.category_info = {'id': subcat_id,
                                         'caption': subcat_caption,
                                         'image': image,
                                         }
        self.controller.widget.add_category_btn.click()
        self.controller.widget.set_selected_category(self.cat_id)
        section_id = 'section_a'
        self.controller.section_id = section_id
        self.controller.widget.add_section_btn.click()
        self.assertIsNone(self.controller.model.get_section_by_id(section_id))

    def test_cannot_add_subcategory_to_category_with_sections(self):
        section_id = 'section_a'
        self.controller.section_id = section_id
        self.controller.widget.add_section_btn.click()

        self.controller.widget.set_selected_category(self.cat_id)

        subcat_id = 'test_sub_cat'
        subcat_caption = 'sub cat!'
        image = os.path.join(data_path, "images/beam_status.png")

        self.controller.category_info = {'id': subcat_id,
                                         'caption': subcat_caption,
                                         'image': image,
                                         }
        self.controller.widget.add_category_btn.click()
        self.assertIsNone(self.controller.model.get_category_by_id(subcat_id))

    def test_cannot_add_subcategory_in_section(self):
        section_id = 'section_a'
        self.controller.section_id = section_id
        self.controller.widget.add_section_btn.click()

        subcat_id = 'test_sub_cat'
        subcat_caption = 'sub cat!'
        image = os.path.join(data_path, "images/beam_status.png")

        self.controller.category_info = {'id': subcat_id,
                                         'caption': subcat_caption,
                                         'image': image,
                                         }
        self.controller.widget.add_category_btn.click()
        self.assertIsNone(self.controller.model.get_category_by_id(subcat_id))

    def test_adding_section_when_section_selected_adds_section_to_parent_category(self):
        section_id = 'section_a'
        self.controller.section_id = section_id
        self.controller.widget.add_section_btn.click()
        self.assertEqual(self.controller.model.section_counter(self.cat_id), 1)

        section_id = 'section_b'
        self.controller.section_id = section_id
        self.controller.widget.add_section_btn.click()
        self.assertEqual(self.controller.model.section_counter(self.cat_id), 2)
