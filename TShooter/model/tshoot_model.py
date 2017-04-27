from qtpy import QtCore
from collections import OrderedDict
from .ts_model import TroubleSection
import os
import yaml


class TroubleShooter(QtCore.QObject):
    def __init__(self, category_id="name", level=0, parent=None):
        super(TroubleShooter, self).__init__()
        self._all_categories = OrderedDict()
        self._main_category = {'id': category_id,  # perhaps id is redundant
                               'level': level,
                               'parent': parent,
                               'caption': 'main',
                               'image': None}
        self._main_category['subcategories'] = OrderedDict()
        self._all_categories[category_id] = self._main_category

    def subcategory_counter(self, category_id):
        return len(self._all_categories[category_id]['subcategories'])

    def add_subcategory(self, category_id, subcategory_id, subcategory_caption, subcategory_image):
        self._all_categories[category_id]['subcategories'][subcategory_id] = {}
        self._all_categories[category_id]['subcategories'][subcategory_id]['id'] = subcategory_id
        self._all_categories[category_id]['subcategories'][subcategory_id]['caption'] = subcategory_caption
        self._all_categories[category_id]['subcategories'][subcategory_id]['image'] = subcategory_image
        self._all_categories[category_id]['subcategories'][subcategory_id]['parent'] = category_id
        self._all_categories[category_id]['subcategories'][subcategory_id]['level'] = \
            self._all_categories[category_id]['level'] + 1
        self._all_categories[subcategory_id] = self._all_categories[category_id]['subcategories'][subcategory_id]

        # self._subcategories[subcategory_name]['obj'] = TroubleCategory(category_id=subcategory_name,
        #                                                                level=self._level + 1, parent=self._id)
        # self._subcategories[subcategory_name]['subcategory_caption'] = subcategory_caption
        # self._subcategories[subcategory_name]['subcategory_image'] = subcategory_image
        return self._all_categories[subcategory_id]