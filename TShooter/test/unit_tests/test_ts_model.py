import unittest
import os
import numpy as np
from mock import MagicMock

from ..utility import QtTest
from ...model.ts_model import TroubleSection, IMAGE, TEXT

unittest_path = os.path.dirname(__file__)
data_path = os.path.join(unittest_path, '../data')


class TroubleSectionTest(QtTest):
    def setUp(self):
        self.model = TroubleSection(section_id="check_problem_a")

    def tearDown(self):
        del self.model

    def test_message_counter(self):
        next_ind = self.model.message_counter
        self.assertEqual(next_ind, 0)
        self.model.add_message("test")
        next_ind = self.model.message_counter
        self.assertEqual(next_ind, 1)

    def test_add_text_message(self):
        msg1 = "test message"
        next_ind = self.model.message_counter
        self.model.add_message(msg1)
        self.assertEqual(self.model.get_message(next_ind), msg1)
        self.assertEqual(self.model.get_message_type(next_ind), TEXT)

    def test_add_image_as_message(self):
        img1 = os.path.join(data_path, "images/beam_status.png")
        next_ind = self.model.message_counter
        self.model.add_message(img1)
        self.assertEqual(self.model.get_message(next_ind), img1)
        self.assertEqual(self.model.get_message_type(next_ind), IMAGE)

    def test_add_multiple_messages(self):
        self.test_add_text_message()
        self.test_add_image_as_message()
        self.test_add_image_as_message()
        self.test_add_text_message()
        next_ind = self.model.message_counter
        self.assertEqual(next_ind, 4)

    def test_choice_counter(self):
        next_ind = self.model.choice_counter
        self.assertEqual(next_ind, 0)
        self.model.add_choice("test", solution_type="message", solution="no problem")
        next_ind = self.model.choice_counter
        self.assertEqual(next_ind, 1)

    def test_add_choice_with_message_as_solution(self):
        choice1 = "yes"
        solution1_type = "message"
        solution1 = "fix problem a"

        next_ind = self.model.choice_counter
        self.model.add_choice(choice1, solution_type=solution1_type, solution=solution1)
        self.assertEqual(self.model.get_choice(next_ind), choice1)
        self.assertEqual(self.model.get_solution_type(next_ind), solution1_type)
        self.assertEqual(self.model.get_solution_message(next_ind), solution1)
        self.assertEqual(self.model.get_solution_section_id(next_ind), None)

    def test_add_choice_with_section_as_solution(self):
        self.next_section = TroubleSection(section_id="check_problem_b")
        choice1 = "yes"
        solution1_type = "section"

        next_ind = self.model.choice_counter
        self.model.add_choice(choice1, solution_type=solution1_type, solution=self.next_section.id)
        self.assertEqual(self.model.get_choice(next_ind), choice1)
        self.assertEqual(self.model.get_solution_type(next_ind), solution1_type)
        self.assertEqual(self.model.get_solution_message(next_ind), "Next")
        self.assertEqual(self.model.get_solution_section_id(next_ind), self.next_section.id)

    def test_add_multiple_choices(self):
        self.test_add_choice_with_message_as_solution()
        self.test_add_choice_with_section_as_solution()
        self.test_add_choice_with_message_as_solution()
        self.test_add_choice_with_section_as_solution()
        next_ind = self.model.choice_counter
        self.assertEqual(next_ind, 4)

