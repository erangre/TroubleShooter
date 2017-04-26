import unittest
import os
import numpy as np
from mock import MagicMock

from ..utility import QtTest
from ...model.cat_model import TroubleCategory
from ...model.ts_model import TroubleSection

unittest_path = os.path.dirname(__file__)
data_path = os.path.join(unittest_path, '../data')


class TroubleCategoryTest(QtTest):
    def setUp(self):
        self.model = TroubleCategory(category_id="category_a", level=1)

    def tearDown(self):
        del self.model

    def test_section_counter(self):
        next_ind = self.model.section_counter
        self.assertEqual(next_ind, 0)
        self.model.add_section("section_a", "first section")
        next_ind = self.model.section_counter
        self.assertEqual(next_ind, 1)

    def test_subcategory_counter(self):
        new_subcategory_image = os.path.join(data_path, "images/beam_status.png")
        next_ind = self.model.subcategory_counter
        self.assertEqual(next_ind, 0)
        self.model.add_subcategory("subcategory_a", "first category", new_subcategory_image)
        next_ind = self.model.subcategory_counter
        self.assertEqual(next_ind, 1)

    def test_add_section_to_category(self):
        new_section_name = "section_a"
        new_section_caption = "First problem to check"
        # next_ind = self.model.section_counter
        new_section = self.model.add_section(new_section_name, new_section_caption)  # type: TroubleSection
        self.assertEqual(new_section['obj'].id, new_section_name)
        self.assertEqual(new_section['obj'].parent_id, self.model.id)
        self.assertEqual(new_section['obj'].level, self.model.level + 1)

    def test_add_subcategory_to_category(self):
        new_subcategory_name = "subcategory_a"
        new_subcategory_caption = "The first category of problems"
        new_subcategory_image = os.path.join(data_path, "images/beam_status.png")
        # next_ind = self.model.subcategory_counter
        new_subcategory = self.model.add_subcategory(new_subcategory_name, new_subcategory_caption,
                                                     new_subcategory_image)  # type: TroubleCategory
        self.assertEqual(new_subcategory['obj'].id, new_subcategory_name)
        self.assertEqual(new_subcategory['obj'].parent_id, self.model.id)
        self.assertEqual(new_subcategory['obj'].level, self.model.level + 1)

    def test_add_section_to_subcategory(self):
        new_subcategory_name = "subcategory_a"
        new_subcategory_caption = "The first category of problems"
        new_subcategory_image = os.path.join(data_path, "images/beam_status.png")
        # next_ind = self.model.subcategory_counter
        new_subcategory = self.model.add_subcategory(new_subcategory_name, new_subcategory_caption,
                                                     new_subcategory_image)  # type: TroubleCategory

        new_section_name = "section_a"
        new_section_caption = "First problem to check"
        next_ind = new_subcategory['obj'].section_counter
        new_section = new_subcategory['obj'].add_section(new_section_name, new_section_caption)  # type: TroubleSection
        self.assertEqual(new_section['obj'].id, new_section_name)
        self.assertEqual(new_section['obj'].parent_id, new_subcategory['obj'].id)
        self.assertEqual(new_section['obj'].level, new_subcategory['obj'].level + 1)
