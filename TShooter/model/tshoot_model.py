from qtpy import QtCore
from collections import OrderedDict
from .ts_model import TroubleSection
import os
import yaml
import copy
TEXT = 0
IMAGE = 1
SECTION_SOLUTION = "Next"


class TroubleShooter(QtCore.QObject):
    def __init__(self, category_id="name", level=0, parent=None):
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
        new_category['id'] = subcategory_id  # redundant?
        new_category['caption'] = subcategory_caption
        new_category['image'] = subcategory_image
        new_category['parent_id'] = category_id
        new_category['level'] = self._all_categories[category_id]['level'] + 1
        new_category['subcategories'] = OrderedDict()
        self._all_categories[subcategory_id] = new_category

        self._all_categories[subcategory_id]['sections'] = OrderedDict()

        return self._all_categories[subcategory_id]

    def section_counter(self, category_id):
        return len(self._all_categories[category_id]['sections'])

    def add_section_to_category(self, category_id, section_id, section_caption):
        if section_id in self._all_sections:
            return None
        self._all_categories[category_id]['sections'][section_id] = {}
        new_section = self._all_categories[category_id]['sections'][section_id]
        new_section['id'] = section_id  # redundant?
        new_section['caption'] = section_caption
        new_section['parent_id'] = category_id
        new_section['level'] = self._all_categories[category_id]['level'] + 1
        new_section['messages'] = []
        new_section['message_type'] = []
        new_section['choices'] = []
        new_section['solution_type'] = []
        new_section['solution_message'] = []
        new_section['solution_section_id'] = []

        self._all_sections[section_id] = new_section

        return self._all_sections[section_id]

    def get_section_by_id(self, section_id):
        return self._all_sections.get(section_id, None)

    def message_counter(self, section_id):
        return len(self._all_sections[section_id]['messages'])

    def add_message_to_section(self, section_id, message):
        self._all_sections[section_id]['messages'].append(message)
        if os.path.isfile(message):
            self._all_sections[section_id]['message_type'].append(IMAGE)
        else:
            self._all_sections[section_id]['message_type'].append(TEXT)

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
