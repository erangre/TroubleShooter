import unittest
import os
import numpy as np
from mock import MagicMock
import yaml

from ..utility import QtTest
# from ...model.cat_model import TroubleCategory
# from ...model.ts_model import TroubleSection
from ...model.tshoot_model import TroubleShooter

unittest_path = os.path.dirname(__file__)
data_path = os.path.join(unittest_path, '../data')


class TroubleCategoryTest(QtTest):
    def setUp(self):
        self.model = TroubleShooter(category_id="main", level=0)

    def tearDown(self):
        del self.model

    def test_subcategory_counter(self):
        new_subcategory_image = os.path.join(data_path, "images/beam_status.png")
        next_ind = self.model.subcategory_counter("main")
        self.assertEqual(next_ind, 0)
        self.model.add_subcategory("main", "subcategory_a", "first category", new_subcategory_image)
        next_ind = self.model.subcategory_counter("main")
        self.assertEqual(next_ind, 1)

    def test_add_subcategory_to_category(self):
        main_category_id = "main"
        main_category = self.model.get_category_by_id(main_category_id)

        new_sub_a_id = "subcategory_a"
        new_sub_a_caption = "The first category of problems"
        new_sub_a_image = os.path.join(data_path, "images/beam_status.png")

        new_sub_a = self.model.add_subcategory(main_category_id, new_sub_a_id, new_sub_a_caption, new_sub_a_image)
        self.assertEqual(new_sub_a['id'], new_sub_a_id)
        self.assertEqual(new_sub_a['parent_id'], main_category_id)
        self.assertEqual(new_sub_a['level'], main_category['level'] + 1)

        new_sub_b_id = "subcategory_b"
        new_sub_b_caption = "The first subcategory of problems"
        new_sub_b_image = os.path.join(data_path, "images/beam_status.png")

        new_sub_b = self.model.add_subcategory(new_sub_a_id, new_sub_b_id, new_sub_b_caption, new_sub_b_image)
        self.assertEqual(new_sub_b['id'], new_sub_b_id)
        self.assertEqual(new_sub_b['parent_id'], new_sub_a_id)
        self.assertEqual(new_sub_b['level'], new_sub_a['level'] + 1)

    def test_add_existing_category_id_results_in_None(self):
        main_category_id = "main"
        main_category = self.model.get_category_by_id(main_category_id)

        new_sub_a_id = "subcategory_a"
        new_sub_a_caption = "The first category of problems"
        new_sub_a_image = os.path.join(data_path, "images/beam_status.png")

        new_sub_a = self.model.add_subcategory(main_category_id, new_sub_a_id, new_sub_a_caption, new_sub_a_image)

        new_sub_b_id = "subcategory_a"
        new_sub_b_caption = "The first subcategory of problems"
        new_sub_b_image = os.path.join(data_path, "images/beam_status.png")

        new_sub_b = self.model.add_subcategory(new_sub_a_id, new_sub_b_id, new_sub_b_caption, new_sub_b_image)

        self.assertIsNone(new_sub_b)


class TroubleSectionCreationTest(QtTest):
    def setUp(self):
        self.model = TroubleShooter(category_id="main", level=0)
        self.main_category_id = "main"
        new_subcategory_image = os.path.join(data_path, "images/beam_status.png")
        self.new_subcategory_id = "subcategory_a"
        new_subcategory_caption = "first category"
        self.new_subcategory = self.model.add_subcategory(self.main_category_id, self.new_subcategory_id,
                                                          new_subcategory_caption, new_subcategory_image)

    def tearDown(self):
        del self.model

    def test_section_counter(self):
        new_section_id = "section_a"
        new_section_caption = "first section"
        next_ind = self.model.section_counter(self.new_subcategory_id)
        self.assertEqual(next_ind, 0)
        self.model.add_section_to_category(self.new_subcategory_id, new_section_id, new_section_caption)
        next_ind = self.model.section_counter(self.new_subcategory_id)
        self.assertEqual(next_ind, 1)

    def test_add_section_to_category(self):
        new_section_id = "section_a"
        new_section_caption = "First problem to check"
        new_section = self.model.add_section_to_category(self.new_subcategory_id, new_section_id, new_section_caption)

        self.assertEqual(new_section['id'], new_section_id)
        self.assertEqual(new_section['parent_id'], self.new_subcategory_id)
        self.assertEqual(new_section['level'], self.new_subcategory['level'] + 1)

    def test_add_existing_section_id_results_in_None(self):
        new_sub_b_id = "subcategory_b"
        new_sub_b_caption = "The first subcategory of problems"
        new_sub_b_image = os.path.join(data_path, "images/beam_status.png")

        new_sub_b = self.model.add_subcategory(self.main_category_id, new_sub_b_id, new_sub_b_caption, new_sub_b_image)

        new_section_a_id = "section_a"
        new_section_a_caption = "First problem to check"
        new_section_a = self.model.add_section_to_category(self.new_subcategory_id, new_section_a_id,
                                                           new_section_a_caption)
        self.assertIsNotNone(new_section_a)

        new_section_b_id = "section_a"
        new_section_b_caption = "Second problem to check"
        new_section_b = self.model.add_section_to_category(new_sub_b_id, new_section_b_id, new_section_b_caption)

        self.assertIsNone(new_section_b)




class TroubleSectionTest(QtTest):
    def setUp(self):
        self.model = TroubleShooter(category_id="main", level=0)
        self.main_category_id = "main"
        new_subcategory_image = os.path.join(data_path, "images/beam_status.png")
        self.new_subcategory_id = "subcategory_a"
        new_subcategory_caption = "first category"
        self.new_subcategory = self.model.add_subcategory(self.main_category_id, self.new_subcategory_id,
                                                          new_subcategory_caption, new_subcategory_image)

        self.new_section_id = "section_a"
        new_section_caption = "First problem to check"
        self.new_section = self.model.add_section_to_category(self.new_subcategory_id, self.new_section_id,
                                                              new_section_caption)

    def tearDown(self):
        del self.model

    def test_message_counter(self):
        next_ind = self.model.message_counter(self.new_section_id)
        self.assertEqual(next_ind, 0)
        self.model.add_message_to_section(self.new_section_id, "test message")
        next_ind = self.model.message_counter(self.new_section_id)
        self.assertEqual(next_ind, 1)


# class MainCategoryTest(QtTest):
#     def setUp(self):
#         self.cat_model = TroubleCategory(category_id="main", level=0)
#
#     def tearDown(self):
#         del self.cat_model
#
#     def test_export_category_to_yaml(self):
#         new_subcategory_name = "subcategory_a"
#         new_subcategory_caption = "The first category of problems"
#         new_subcategory_image = os.path.join(data_path, "images/beam_status.png")
#         # self.cat_model.add_subcategory(new_subcategory_name, new_subcategory_caption, new_subcategory_image)
#
#         output_file = os.path.join(data_path, 'output1.yml')
#         self.cat_model.export_category_to_yaml(output_file)
#         self.assertTrue(os.path.isfile(output_file))
#
#         # outfile = open(output_file, 'r')
#         # output_contents = outfile.readlines()
#         # self.assertTrue(new_subcategory_name in '-'.join(output_contents))
#
#     def test_import_category_from_yaml(self):
#         new_subcategory_name = "subcategory_a"
#         new_subcategory_caption = "The first category of problems"
#         new_subcategory_image = os.path.join(data_path, "images/beam_status.png")
#         self.cat_model.add_subcategory(new_subcategory_name, new_subcategory_caption, new_subcategory_image)
#
#         output_file = os.path.join(data_path, 'output1.yml')
#         self.cat_model.export_category_to_yaml(output_file)
#         self.assertTrue(os.path.isfile(output_file))
#
#         self.tearDown()
#         self.setUp()
#
#         self.cat_model.import_category_from_yaml(output_file)
#
#         # os.remove(output_file)
