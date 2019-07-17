import copy
import os
import re
from collections import OrderedDict
from .config import highlight_strings

import yaml
from qtpy import QtCore

TEXT = 0
IMAGE = 1
PV = 2
SOLUTION_TYPES = ('message', 'section')
SECTION_SOLUTION = "Click Next"


class TroubleShooter(QtCore.QObject):
    def __init__(self, category_id="main", level=0, parent=None):
        super(TroubleShooter, self).__init__()
        self._all_categories = OrderedDict()
        self._all_sections = OrderedDict()
        self._main_category = {'id': category_id,  # perhaps id is redundant
                               'level': level,
                               'parent_id': parent,
                               'caption': 'main',
                               'image': None,
                               'sections': None,
                               'subcategories': OrderedDict()}
        self._all_categories[category_id] = self._main_category
        self.search_string = ''

    def subcategory_counter(self, category_id):
        return len(self._all_categories[category_id]['subcategories'])

    def get_category_by_id(self, category_id):
        return self._all_categories.get(category_id, None)

    def add_subcategory(self, category_id, subcategory_id, subcategory_caption, subcategory_image):
        if subcategory_id in self._all_categories:
            return None
        self._all_categories[category_id]['subcategories'][subcategory_id] = {}
        new_category = self._all_categories[category_id]['subcategories'][subcategory_id]
        new_category['id'] = subcategory_id
        new_category['caption'] = subcategory_caption
        new_category['image'] = subcategory_image
        new_category['parent_id'] = category_id
        new_category['level'] = self._all_categories[category_id]['level'] + 1
        new_category['subcategories'] = OrderedDict()
        self._all_categories[subcategory_id] = new_category

        self._all_categories[subcategory_id]['sections'] = OrderedDict()

        return self._all_categories[subcategory_id]

    def edit_category(self, category_id, subcat_caption, subcat_image):
        self._all_categories[category_id]['caption'] = subcat_caption
        self._all_categories[category_id]['image'] = subcat_image

    def remove_category(self, category_id):
        parent_category_id = self._all_categories[category_id]['parent_id']
        del self._all_categories[parent_category_id]['subcategories'][category_id]
        del self._all_categories[category_id]
        return parent_category_id

    def move_category(self, parent_cat_id, category_id, direction):
        parent_cat = self.get_category_by_id(parent_cat_id)
        category_ind = list(parent_cat['subcategories'].keys()).index(category_id)
        categories_list = list(parent_cat['subcategories'].items())
        if direction == 'up' and category_ind > 0:
            categories_list.insert(category_ind - 1, categories_list.pop(category_ind))
        elif direction == 'down' and category_ind < len(categories_list) - 1:
            categories_list.insert(category_ind + 1, categories_list.pop(category_ind))
        parent_cat['subcategories'] = OrderedDict(categories_list)

    def section_counter(self, category_id):
        return len(self._all_categories[category_id]['sections'])

    def all_section_counter(self):
        return len(self._all_sections)

    def add_section_to_category(self, category_id, section_id, section_caption):
        if section_id in self._all_sections:
            return None
        self._all_categories[category_id]['sections'][section_id] = {}
        new_section = self._all_categories[category_id]['sections'][section_id]
        new_section['id'] = section_id
        new_section['caption'] = section_caption
        new_section['parent_id'] = category_id
        new_section['level'] = self._all_categories[category_id]['level'] + 1
        new_section['messages'] = []
        new_section['message_type'] = []
        new_section['message_pv'] = []
        new_section['choices'] = []
        new_section['solution_type'] = []
        new_section['solution_message'] = []
        new_section['solution_section_id'] = []

        self._all_sections[section_id] = new_section

        return self._all_sections[section_id]

    def remove_section(self, section_id):
        parent_category_id = self._all_sections[section_id]['parent_id']
        del self._all_categories[parent_category_id]['sections'][section_id]
        del self._all_sections[section_id]
        return parent_category_id

    def get_section_by_id(self, section_id):
        return self._all_sections.get(section_id, None)

    def edit_section(self, old_section_id, new_section_id):
        section = self.get_section_by_id(old_section_id)
        section['id'] = new_section_id
        section['caption'] = new_section_id
        parent_id = section['parent_id']
        parent_cat = self.get_category_by_id(parent_id)
        parent_cat['sections'] = OrderedDict(
            (new_section_id if k == old_section_id else k, v) for k, v in parent_cat['sections'].items())
        self._all_sections = OrderedDict(
            (new_section_id if k == old_section_id else k, v) for k, v in self._all_sections.items())
        for section in self._all_sections:
            self._all_sections[section]['solution_section_id'] = \
                [new_section_id if sec == old_section_id else
                 sec for sec in self._all_sections[section]['solution_section_id']]

    def move_section(self, parent_cat_id, section_id, direction):
        parent_cat = self.get_category_by_id(parent_cat_id)
        section_ind = list(parent_cat['sections'].keys()).index(section_id)
        sections_list = list(parent_cat['sections'].items())
        if direction == 'up' and section_ind > 0:
            sections_list.insert(section_ind - 1, sections_list.pop(section_ind))
        elif direction == 'down' and section_ind < len(sections_list) - 1:
            sections_list.insert(section_ind + 1, sections_list.pop(section_ind))
        parent_cat['sections'] = OrderedDict(sections_list)

    def message_counter(self, section_id):
        return len(self._all_sections[section_id]['messages'])

    def add_message_to_section(self, section_id, message, message_type, pv=None):
        self._all_sections[section_id]['messages'].append(message)
        if message_type == IMAGE and os.path.isfile(message):
            self._all_sections[section_id]['message_type'].append(IMAGE)
            self._all_sections[section_id]['message_pv'].append(None)
            return True
        elif message_type == TEXT and message:
            self._all_sections[section_id]['message_type'].append(TEXT)
            self._all_sections[section_id]['message_pv'].append(None)
            return True
        elif message_type == PV and message:
            self._all_sections[section_id]['message_type'].append(PV)
            self._all_sections[section_id]['message_pv'].append(pv)
        else:
            return False

    def remove_message_from_section(self, section_id, ind):
        self._all_sections[section_id]['messages'].pop(ind)
        self._all_sections[section_id]['message_type'].pop(ind)
        self._all_sections[section_id]['message_pv'].pop(ind)

    def modify_message_in_section(self, section_id, ind, new_message):
        self._all_sections[section_id]['messages'][ind] = new_message

    def modify_message_pv_in_section(self, section_id, ind, new_pv):
        self._all_sections[section_id]['message_pv'][ind] = new_pv

    def move_message_up(self, section_id, ind):
        current_section = self.get_section_by_id(section_id)
        if ind > 0:
            current_section['messages'].insert(ind - 1, current_section['messages'].pop(ind))
            current_section['message_type'].insert(ind - 1, current_section['message_type'].pop(ind))
            current_section['message_pv'].insert(ind - 1, current_section['message_pv'].pop(ind))

    def move_message_down(self, section_id, ind):
        current_section = self.get_section_by_id(section_id)
        if ind < len(current_section['messages']):
            current_section['messages'].insert(ind + 1, current_section['messages'].pop(ind))
            current_section['message_type'].insert(ind + 1, current_section['message_type'].pop(ind))
            current_section['message_pv'].insert(ind + 1, current_section['message_pv'].pop(ind))

    def choice_counter(self, section_id):
        return len(self._all_sections[section_id]['choices'])

    def add_choice_to_section(self, section_id, choice_caption, **kwargs):
        self._all_sections[section_id]['choices'].append(choice_caption)
        solution_type = kwargs['solution_type']
        self._all_sections[section_id]['solution_type'].append(solution_type)
        if solution_type == 'message':
            self._all_sections[section_id]['solution_message'].append(kwargs['solution'])
            self._all_sections[section_id]['solution_section_id'].append(None)
            return True
        elif solution_type == 'section':
            self._all_sections[section_id]['solution_message'].append(SECTION_SOLUTION)
            self._all_sections[section_id]['solution_section_id'].append(kwargs['solution'])
            return True
        else:
            return False

    def remove_choice_from_section(self, section_id, ind):
        self._all_sections[section_id]['choices'].pop(ind)
        self._all_sections[section_id]['solution_type'].pop(ind)
        self._all_sections[section_id]['solution_message'].pop(ind)
        self._all_sections[section_id]['solution_section_id'].pop(ind)

    def modify_choice_in_section(self, section_id, row, new_choice_text):
        self._all_sections[section_id]['choices'][row] = new_choice_text

    def modify_solution_message_in_section(self, section_id, row, new_message_text):
        self._all_sections[section_id]['solution_message'][row] = new_message_text

    def modify_solution_section_in_section(self, section_id, row, new_solution):
        self._all_sections[section_id]['solution_section_id'][row] = new_solution

    def move_choice_up(self, section_id, ind):
        current_section = self.get_section_by_id(section_id)
        if ind > 0:
            current_section['choices'].insert(ind - 1, current_section['choices'].pop(ind))
            current_section['solution_type'].insert(ind - 1, current_section['solution_type'].pop(ind))
            current_section['solution_message'].insert(ind - 1, current_section['solution_message'].pop(ind))
            current_section['solution_section_id'].insert(ind - 1, current_section['solution_section_id'].pop(ind))

    def move_choice_down(self, section_id, ind):
        current_section = self.get_section_by_id(section_id)
        if ind < len(current_section['choices']):
            current_section['choices'].insert(ind + 1, current_section['choices'].pop(ind))
            current_section['solution_type'].insert(ind + 1, current_section['solution_type'].pop(ind))
            current_section['solution_message'].insert(ind + 1, current_section['solution_message'].pop(ind))
            current_section['solution_section_id'].insert(ind + 1, current_section['solution_section_id'].pop(ind))

    def get_all_sections_formatted(self):
        all_sections_formatted = []
        for section in self._all_sections.values():
            all_sections_formatted.append(section['parent_id'] + ':' + section['id'])

        return all_sections_formatted

    def get_all_data(self):
        all_data = {'all_categories': self._all_categories,
                    'all_sections': self._all_sections}
        return all_data

    def export_category_to_yaml(self, output_file):
        all_data = copy.deepcopy(self.get_all_data())

        for section in all_data['all_sections']:
            section_data = all_data['all_sections'][section]
            for ind in range(len(section_data['messages'])):
                if section_data['message_type'][ind] == IMAGE:
                    section_data['messages'][ind] = os.path.relpath(section_data['messages'][ind],
                                                                    os.path.dirname(output_file))

        for category in all_data['all_categories']:
            cat_data = all_data['all_categories'][category]
            if cat_data['image'] is not None and cat_data['image'] is not '':
                cat_data['image'] = os.path.relpath(cat_data['image'], os.path.dirname(output_file))

        stream = open(output_file, "w")
        yaml.dump(all_data, stream)
        stream.close()
        del all_data

    def import_category_from_yaml(self, input_file):
        stream = open(input_file, 'r')
        all_data = yaml.full_load(stream)
        self._all_categories = copy.deepcopy(all_data['all_categories'])
        self._all_sections = copy.deepcopy(all_data['all_sections'])

        for section in self._all_sections:
            section_data = self._all_sections[section]
            for ind in range(len(section_data['messages'])):
                if section_data['message_type'][ind] == IMAGE:
                    section_data['messages'][ind] = os.path.normpath(os.path.join(os.path.dirname(input_file),
                                                                                  section_data['messages'][ind]))

        for category in self._all_categories:
            cat_data = self._all_categories[category]
            if cat_data['image'] is not None:
                cat_data['image'] = os.path.normpath(os.path.join(os.path.dirname(input_file),
                                                                  cat_data['image']))

    def find_string_in_section_captions(self, search_string):
        search_results = []
        for section_id in self._all_sections:
            section = self.get_section_by_id(section_id)
            if re.search(search_string, section['caption'], re.IGNORECASE):
                search_results.append({'id': section['id'], 'text': section['caption'], 'type': 'section_caption'})
        return search_results

    def find_string_in_section_messages(self, search_string):
        search_results = []
        for section_id in self._all_sections:
            section = self.get_section_by_id(section_id)
            for ind, message in enumerate(section['messages']):
                if re.search(search_string, message, re.IGNORECASE):
                    if section['message_type'][ind] == TEXT:
                        message_type = 'section_message'
                    elif section['message_type'][ind] == IMAGE:
                        message_type = 'image_path'
                    elif section['message_type'][ind] == PV:
                        message_type = 'pv_message'
                    search_results.append({'id': section['id'], 'text': section['messages'][ind],
                                           'type': message_type})
                if not section['message_pv'][ind] is None and search_string in section['message_pv'][ind]:
                    search_results.append({'id': section['id'], 'text': section['message_pv'][ind],
                                           'type': 'epics_pv'})
        return search_results

    def find_string_in_solution_messages(self, search_string):
        search_results = []
        for section_id in self._all_sections:
            section = self.get_section_by_id(section_id)
            for ind, message in enumerate(section['solution_message']):
                if re.search(search_string, message, re.IGNORECASE):
                    search_results.append({'id': section['id'], 'text': section['solution_message'][ind],
                                           'type': 'solution_message'})
        return search_results

    def find_search_string_in_all(self, search_string):
        # TODO: make search have more options, such as only sections containing a few different strings
        search_results = self.find_string_in_section_captions(search_string) + \
                         self.find_string_in_section_messages(search_string) + \
                         self.find_string_in_solution_messages(search_string)
        return search_results

    def format_msg(self, msg):
        msg = msg.replace('\\n', '\n').replace('\\t', '\t')
        for custom_highlight in highlight_strings:
            start_input = highlight_strings[custom_highlight]['start']['input']
            start_output = highlight_strings[custom_highlight]['start']['output']
            end_input = highlight_strings[custom_highlight]['end']['input']
            end_output = highlight_strings[custom_highlight]['end']['output']
            msg = msg.replace(start_input, start_output)
            msg = msg.replace(end_input, end_output)
        return msg
