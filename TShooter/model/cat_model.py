from qtpy import QtCore
from collections import OrderedDict
from .ts_model import TroubleSection
import os
import yaml


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

    # def export_category_to_yaml(self, output_file):
    #     stream = open(output_file, "w")
    #     yaml.dump(self, stream)
    #     stream.close()

    # def import_category_from_yaml(self, input_file):
        # yaml.add_constructor(u'!python/object:TShooter.model.cat_model.TroubleCategory', self.category_constructor)
        # print(yaml.load(stream, Loader=yaml.Loader))

    # def category_constructor(self, loader, node):
    #     values = loader.construct_mapping(node, deep=True)
    #     _id = values["_id"]
    #     _level = values["_level"]
    #     _parent_id = values["_parent_id"]
    #     _subcategories = values["_subcategories"]
    #     _sections = values["_sections"]
    #     return TroubleCategory(_id, _level, _parent_id)

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
