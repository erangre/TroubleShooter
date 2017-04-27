from qtpy import QtCore
from collections import OrderedDict
from .ts_model import TroubleSection
import os
import yaml


class TroubleShooter(QtCore.QObject):
    def __init__(self, category_id="name", level=0, parent=None):
        super(TroubleShooter, self).__init__()
        self._all_categories = OrderedDict()
        self._all_sections = OrderedDict()
        self._main_category = {'id': category_id,  # perhaps id is redundant
                               'level': level,
                               'parent': parent,
                               'caption': 'main',
                               'image': None,
                               'sections': None,
                               'subcategories': OrderedDict()}
        self._all_categories[category_id] = self._main_category

    def subcategory_counter(self, category_id):
        return len(self._all_categories[category_id]['subcategories'])

    def get_category_by_id(self, category_id):
        return self._all_categories[category_id]

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

        self._all_sections[section_id] = new_section

        return self._all_sections[section_id]

    def message_counter(self, section_id):
        return len(self._all_sections[section_id]['messages'])

    def add_message_to_section(self, section_id, message):
        self._all_sections[section_id]['messages'].append(message)
