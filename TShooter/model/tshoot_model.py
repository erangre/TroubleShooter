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
        self._all_categories[category_id]['subcategories'][subcategory_id]['id'] = subcategory_id  # redundant?
        self._all_categories[category_id]['subcategories'][subcategory_id]['caption'] = subcategory_caption
        self._all_categories[category_id]['subcategories'][subcategory_id]['image'] = subcategory_image
        self._all_categories[category_id]['subcategories'][subcategory_id]['parent_id'] = category_id
        self._all_categories[category_id]['subcategories'][subcategory_id]['level'] = \
            self._all_categories[category_id]['level'] + 1
        self._all_categories[category_id]['subcategories'][subcategory_id]['subcategories'] = OrderedDict()
        self._all_categories[subcategory_id] = self._all_categories[category_id]['subcategories'][subcategory_id]

        self._all_categories[subcategory_id]['sections'] = OrderedDict()

        return self._all_categories[subcategory_id]

    def section_counter(self, category_id):
        return len(self._all_categories[category_id]['sections'])

    def add_section(self, category_id, section_id, section_caption):
        if section_id in self._all_sections:
            return None
        self._all_categories[category_id]['sections'][section_id] = {}
        self._all_categories[category_id]['sections'][section_id]['id'] = section_id  # redundant?
        self._all_categories[category_id]['sections'][section_id]['caption'] = section_caption
        self._all_categories[category_id]['sections'][section_id]['parent_id'] = category_id
        self._all_categories[category_id]['sections'][section_id]['level'] = \
            self._all_categories[category_id]['level'] + 1

        self._all_sections[section_id] = self._all_categories[category_id]['sections'][section_id]

        return self._all_sections[section_id]
