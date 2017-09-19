import copy
import os
from collections import OrderedDict

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

    def remove_category(self, category_id):
        parent_category_id = self._all_categories[category_id]['parent_id']
        del self._all_categories[parent_category_id]['subcategories'][category_id]
        del self._all_categories[category_id]
        return parent_category_id

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

    def get_section_by_id(self, section_id):
        return self._all_sections.get(section_id, None)

    def remove_section(self, section_id):
        parent_category_id = self._all_sections[section_id]['parent_id']
        del self._all_categories[parent_category_id]['sections'][section_id]
        del self._all_sections[section_id]
        return parent_category_id

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
        stream = open(output_file, "w")
        yaml.dump(self.get_all_data(), stream)
        stream.close()

    def import_category_from_yaml(self, input_file):
        stream = open(input_file, 'r')
        all_data = yaml.load(stream)
        self._all_categories = copy.deepcopy(all_data['all_categories'])
        self._all_sections = copy.deepcopy(all_data['all_sections'])
