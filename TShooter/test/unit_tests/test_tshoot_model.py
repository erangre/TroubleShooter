import unittest
import os
import numpy as np
from mock import MagicMock
import yaml
import copy

from ..utility import QtTest
# from ...model.cat_model import TroubleCategory
# from ...model.ts_model import TroubleSection
from ...model.tshoot_model import TroubleShooter, IMAGE, TEXT, PV, SECTION_SOLUTION
from ...model.config import highlight_strings

unittest_path = os.path.dirname(__file__)
data_path = os.path.normpath(os.path.join(unittest_path, '../data'))


class TroubleCategoryTest(QtTest):
    def setUp(self):
        self.model = TroubleShooter(category_id="main", level=0)

    def tearDown(self):
        del self.model

    def helper_add_subcategory(self, parent_category_id, cat_id, caption, image):
        prev_ind = self.model.subcategory_counter(parent_category_id)
        new_sub_cat = self.model.add_subcategory(parent_category_id, cat_id, caption, image)
        next_ind = self.model.subcategory_counter(parent_category_id)
        self.assertEqual(next_ind, prev_ind + 1)
        self.assertEqual(new_sub_cat['id'], cat_id)
        self.assertEqual(new_sub_cat['parent_id'], parent_category_id)
        self.assertEqual(new_sub_cat['level'], self.model.get_category_by_id(parent_category_id)['level'] + 1)

    def test_subcategory_counter(self):
        new_subcategory_image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        self.helper_add_subcategory("main", "subcategory_a", "first category", new_subcategory_image)

    def test_add_subcategory_to_category(self):
        main_category_id = "main"

        new_sub_a_id = "subcategory_a"
        new_sub_a_caption = "The first category of problems"
        new_sub_a_image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        self.helper_add_subcategory(main_category_id, new_sub_a_id, new_sub_a_caption, new_sub_a_image)

        new_sub_b_id = "subcategory_b"
        new_sub_b_caption = "The first subcategory of problems"
        new_sub_b_image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        self.helper_add_subcategory(main_category_id, new_sub_b_id, new_sub_b_caption, new_sub_b_image)

    def test_add_existing_category_id_results_in_None(self):
        main_category_id = "main"
        main_category = self.model.get_category_by_id(main_category_id)

        new_sub_a_id = "subcategory_a"
        new_sub_a_caption = "The first category of problems"
        new_sub_a_image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))

        new_sub_a = self.model.add_subcategory(main_category_id, new_sub_a_id, new_sub_a_caption, new_sub_a_image)

        new_sub_b_id = "subcategory_a"
        new_sub_b_caption = "The first subcategory of problems"
        new_sub_b_image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))

        new_sub_b = self.model.add_subcategory(new_sub_a_id, new_sub_b_id, new_sub_b_caption, new_sub_b_image)

        self.assertIsNone(new_sub_b)

    def test_remove_category(self):
        counter = self.model.subcategory_counter("main")
        self.assertEqual(counter, 0)
        main_category_id = "main"
        main_category = self.model.get_category_by_id(main_category_id)

        new_sub_a_id = "subcategory_a"
        new_sub_a_caption = "The first category of problems"
        new_sub_a_image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))

        new_sub_a = self.model.add_subcategory(main_category_id, new_sub_a_id, new_sub_a_caption, new_sub_a_image)
        counter = self.model.subcategory_counter("main")
        self.assertEqual(counter, 1)

        parent_category = self.model.remove_category(new_sub_a_id)
        counter = self.model.subcategory_counter(parent_category)
        self.assertEqual(counter, 0)


class TroubleSectionCreationTest(QtTest):
    def setUp(self):
        self.model = TroubleShooter(category_id="main", level=0)
        self.main_category_id = "main"
        new_subcategory_image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
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
        self.assertEqual(self.model.all_section_counter(), 1)

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
        new_sub_b_image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))

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

    def test_get_all_sections_formatted(self):
        new_section_id_a = "section_a"
        new_section_caption = "First problem to check"
        new_section_a = self.model.add_section_to_category(self.new_subcategory_id, new_section_id_a, new_section_caption)

        new_section_id_b = "section_b"
        new_section_caption = "Second problem to check"
        new_section_b = self.model.add_section_to_category(self.new_subcategory_id, new_section_id_b, new_section_caption)

        all_sections = self.model.get_all_sections_formatted()
        self.assertEqual(all_sections[0], self.new_subcategory_id + ':' + new_section_id_a)
        self.assertEqual(all_sections[1], self.new_subcategory_id + ':' + new_section_id_b)

    def test_remove_section(self):
        next_ind = self.model.section_counter(self.new_subcategory_id)
        self.assertEqual(next_ind, 0)
        new_section_id = "section_a"
        new_section_caption = "First problem to check"
        new_section = self.model.add_section_to_category(self.new_subcategory_id, new_section_id, new_section_caption)
        next_ind = self.model.section_counter(self.new_subcategory_id)
        self.assertEqual(next_ind, 1)

        parent_category = self.model.remove_section(new_section_id)
        next_ind = self.model.section_counter(parent_category)
        self.assertEqual(next_ind, 0)


class TroubleSectionTest(QtTest):
    def setUp(self):
        self.model = TroubleShooter(category_id="main", level=0)
        self.main_category_id = "main"
        new_subcategory_image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
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

    def test_get_section_by_id(self):
        current_section = self.model.get_section_by_id(self.new_section_id)
        self.assertEqual(current_section, self.new_section)

    def test_message_counter(self):
        next_ind = self.model.message_counter(self.new_section_id)
        self.assertEqual(next_ind, 0)
        self.model.add_message_to_section(self.new_section_id, "test message", TEXT)
        next_ind = self.model.message_counter(self.new_section_id)
        self.assertEqual(next_ind, 1)

    def test_add_text_message(self):
        msg1 = "test message"
        next_ind = self.model.message_counter(self.new_section_id)
        self.model.add_message_to_section(self.new_section_id, msg1, TEXT)
        self.assertEqual(self.new_section['messages'][next_ind], msg1)
        self.assertEqual(self.new_section['message_type'][next_ind], TEXT)
        self.assertEqual(self.new_section['message_pv'][next_ind], None)

    def test_add_image_as_message(self):
        img1 = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        next_ind = self.model.message_counter(self.new_section_id)
        self.model.add_message_to_section(self.new_section_id, img1, IMAGE)
        self.assertEqual(self.new_section['messages'][next_ind], img1)
        self.assertEqual(self.new_section['message_type'][next_ind], IMAGE)
        self.assertEqual(self.new_section['message_pv'][next_ind], None)

    def test_add_pv_as_message(self):
        msg1 = "this is the value {}"
        pv = "13IDD:m20"
        next_ind = self.model.message_counter(self.new_section_id)
        self.model.add_message_to_section(self.new_section_id, msg1, PV, pv)
        self.assertEqual(self.new_section['messages'][next_ind], msg1)
        self.assertEqual(self.new_section['message_type'][next_ind], PV)
        self.assertEqual(self.new_section['message_pv'][next_ind], pv)

    def test_add_multiple_messages(self):
        self.test_add_text_message()
        self.test_add_image_as_message()
        self.test_add_image_as_message()
        self.test_add_text_message()
        next_ind = self.model.message_counter(self.new_section_id)
        self.assertEqual(next_ind, 4)

    def test_add_message_with_custom_highlight(self):
        for custom_highlight in highlight_strings:
            msg0 = "test_message"
            msg1 = highlight_strings[custom_highlight]['start']['input'] + msg0 + \
                   highlight_strings[custom_highlight]['end']['input']
            next_ind = self.model.message_counter(self.new_section_id)
            self.model.add_message_to_section(self.new_section_id, msg1, TEXT)
            # msg2 = highlight_strings[custom_highlight]['start']['output'] + msg0 + \
            #        highlight_strings[custom_highlight]['end']['output']
            self.assertEqual(self.new_section['messages'][next_ind], msg1)

    def test_choice_counter(self):
        next_ind = self.model.choice_counter(self.new_section_id)
        self.assertEqual(next_ind, 0)
        self.model.add_choice_to_section(self.new_section_id, "test", solution_type="message", solution="no problem")
        next_ind = self.model.choice_counter(self.new_section_id)
        self.assertEqual(next_ind, 1)

    def test_add_choice_with_message_as_solution(self):
        choice1 = "yes"
        solution1_type = "message"
        solution1 = "fix problem a"

        next_ind = self.model.choice_counter(self.new_section_id)
        self.model.add_choice_to_section(self.new_section_id, choice1, solution_type=solution1_type, solution=solution1)

        self.assertEqual(self.new_section['choices'][next_ind], choice1)
        self.assertEqual(self.new_section['solution_type'][next_ind], solution1_type)
        self.assertEqual(self.new_section['solution_message'][next_ind], solution1)
        self.assertEqual(self.new_section['solution_section_id'][next_ind], None)

    def test_add_choice_with_section_as_solution(self):
        next_section_id = "section_b"
        next_section_caption = "Check this next"
        next_section = self.model.add_section_to_category(self.new_subcategory_id, next_section_id,
                                                          next_section_caption)

        choice1 = "nope"
        solution1_type = "section"

        next_ind = self.model.choice_counter(self.new_section_id)

        self.model.add_choice_to_section(self.new_section_id, choice1, solution_type=solution1_type,
                                         solution=next_section_id)

        self.assertEqual(self.new_section['choices'][next_ind], choice1)
        self.assertEqual(self.new_section['solution_type'][next_ind], solution1_type)
        self.assertEqual(self.new_section['solution_message'][next_ind], SECTION_SOLUTION)
        self.assertEqual(self.new_section['solution_section_id'][next_ind], next_section_id)

    def test_edit_section_name(self):
        next_section_id = "section_b"
        next_section_caption = "Check this next"
        next_section = self.model.add_section_to_category(self.new_subcategory_id, next_section_id,
                                                          next_section_caption)

        choice1 = "nope"
        solution1_type = "section"

        next_ind = self.model.choice_counter(self.new_section_id)

        self.model.add_choice_to_section(self.new_section_id, choice1, solution_type=solution1_type,
                                         solution=next_section_id)

        new_next_section_id = "section_c"
        self.model.edit_section(next_section_id, new_next_section_id)

        self.assertEqual(self.new_section['choices'][next_ind], choice1)
        self.assertEqual(self.new_section['solution_type'][next_ind], solution1_type)
        self.assertEqual(self.new_section['solution_message'][next_ind], SECTION_SOLUTION)
        self.assertEqual(self.new_section['solution_section_id'][next_ind], new_next_section_id)

    def test_add_multiple_choices(self):
        self.test_add_choice_with_message_as_solution()
        self.test_add_choice_with_section_as_solution()
        self.test_add_choice_with_message_as_solution()
        self.test_add_choice_with_section_as_solution()
        next_ind = self.model.choice_counter(self.new_section_id)
        self.assertEqual(next_ind, 4)


class YAMLExportImportTest(QtTest):
    def setUp(self):
        self.model = TroubleShooter(category_id="main", level=0)
        self.main_category_id = "main"
        new_subcategory_image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        self.new_subcategory_id = "subcategory_a"
        new_subcategory_caption = "first category"
        self.new_subcategory = self.model.add_subcategory(self.main_category_id, self.new_subcategory_id,
                                                          new_subcategory_caption, new_subcategory_image)

        self.new_section_id = "section_a"
        new_section_caption = "First problem to check"
        self.new_section = self.model.add_section_to_category(self.new_subcategory_id, self.new_section_id,
                                                              new_section_caption)

        self.new_section_b_id = "section_b"
        new_section_b_caption = "2nd problem to check"
        self.new_section_b = self.model.add_section_to_category(self.new_subcategory_id, self.new_section_b_id,
                                                                new_section_b_caption)

        choice1 = "yes"
        solution1_type = "message"
        solution1 = "fix problem a"

        choice2 = "nope"
        solution2_type = "section"
        solution2 = self.new_section_b_id

        self.model.add_choice_to_section(self.new_section_id, choice1, solution_type=solution1_type, solution=solution1)
        self.model.add_choice_to_section(self.new_section_id, choice2, solution_type=solution2_type, solution=solution2)

    def tearDown(self):
        del self.model

    def test_export_category_to_yaml(self):
        output_file = os.path.normpath(os.path.join(data_path, 'output1.yml'))
        self.model.export_category_to_yaml(output_file)
        self.assertTrue(os.path.isfile(output_file))

        outfile = open(output_file, 'r')
        output_contents = outfile.readlines()
        self.assertTrue(self.new_subcategory_id in '-'.join(output_contents))

    def test_import_category_from_yaml(self):
        output_file = os.path.normpath(os.path.join(data_path, 'output1.yml'))
        self.model.export_category_to_yaml(output_file)
        self.assertTrue(os.path.isfile(output_file))
        all_data = copy.deepcopy(self.model.get_all_data())

        self.tearDown()
        self.model = TroubleShooter(category_id="main", level=0)
        self.new_subcategory_id = "subcategory_a"

        self.assertIsNone(self.model.get_category_by_id(self.new_subcategory_id))
        self.model.import_category_from_yaml(output_file)
        self.assertEqual(self.new_subcategory_id, self.model.get_category_by_id(self.new_subcategory_id)['id'])
        self.assertDictEqual(self.model.get_all_data(), all_data)

        # os.remove(output_file)


class SearchTest(QtTest):
    def setUp(self):
        self.model = TroubleShooter(category_id="main", level=0)
        self.main_category_id = "main"
        new_subcategory_image = os.path.normpath(os.path.join(data_path, "images/beam_status.png"))
        self.new_subcategory_id = "subcategory_a"
        new_subcategory_caption = "first category"
        self.new_subcategory = self.model.add_subcategory(self.main_category_id, self.new_subcategory_id,
                                                          new_subcategory_caption, new_subcategory_image)

        self.new_section_id = "section_a"
        new_section_caption = "First problem to check"
        self.new_section = self.model.add_section_to_category(self.new_subcategory_id, self.new_section_id,
                                                              new_section_caption)

        self.new_section_id_b = "section_b"
        new_section_caption = "Second problem to check"
        self.new_section_b = self.model.add_section_to_category(self.new_subcategory_id, self.new_section_id_b,
                                                                new_section_caption)

        msg1 = "test message to fix problem"
        next_ind = self.model.message_counter(self.new_section_id)
        self.model.add_message_to_section(self.new_section_id, msg1, TEXT)

        choice1 = "yes"
        solution1_type = "message"
        solution1 = "fix problem a"

        choice2 = "nope"
        solution2_type = "section"
        solution2 = self.new_section_id_b

        self.model.add_choice_to_section(self.new_section_id, choice1, solution_type=solution1_type, solution=solution1)
        self.model.add_choice_to_section(self.new_section_id, choice2, solution_type=solution2_type, solution=solution2)

    def tearDown(self):
        del self.model

    def test_find_string_in_section_captions(self):
        found_section_captions = self.model.find_string_in_section_captions('prob')
        self.assertEqual(len(found_section_captions), 2)

    def test_find_string_in_section_messages(self):
        found_section_messages = self.model.find_string_in_section_messages('prob')
        self.assertEqual(len(found_section_messages), 1)

    def test_find_string_in_solution_messages(self):
        found_solution_messages = self.model.find_string_in_solution_messages('prob')
        self.assertEqual(len(found_solution_messages), 1)

    def test_find_string_in_all(self):
        found_solution_messages = self.model.find_search_string_in_all('prob')
        self.assertEqual(len(found_solution_messages), 4)

    def test_search_is_not_case_sensitive(self):
        found_solution_messages = self.model.find_search_string_in_all('Prob')
        self.assertEqual(len(found_solution_messages), 4)
