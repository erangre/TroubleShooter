from qtpy import QtCore
from collections import OrderedDict
from .ts_model import TroubleSection
import os


class TroubleCategory(QtCore.QObject):
    def __init__(self, category_id=None, level=0, parent=None):
        super(TroubleCategory, self).__init__()
        self._id = category_id
        self._level = level
        self._parent_id = parent
        self._subcategories = OrderedDict()
        self._sections = OrderedDict()

    def add_section(self, section_name, section_caption):
        self._sections[section_name] = {}
        self._sections[section_name]['obj'] = TroubleSection(section_id=section_name, level=self._level+1,
                                                             parent=self._id)
        self._sections[section_name]['section_caption'] = section_caption
        return self._sections[section_name]

    def add_subcategory(self, subcategory_name, subcategory_caption, subcategory_image):
        self._subcategories[subcategory_name] = {}
        self._subcategories[subcategory_name]['obj'] = TroubleCategory(category_id=subcategory_name,
                                                                       level=self._level+1, parent=self._id)
        self._subcategories[subcategory_name]['subcategory_caption'] = subcategory_caption
        self._subcategories[subcategory_name]['subcategory_image'] = subcategory_image
        return self._subcategories[subcategory_name]

    @property
    def section_counter(self):
        return len(self._sections)

    @property
    def subcategory_counter(self):
        return len(self._subcategories)

    @property
    def id(self):
        return self._id

    @property
    def level(self):
        return self._level

    @property
    def parent_id(self):
        return self._parent_id
