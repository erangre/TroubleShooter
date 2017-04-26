from qtpy import QtCore
import os
IMAGE = 1
TEXT = 0


class TroubleSection(QtCore.QObject):
    def __init__(self, section_id=None, level=1, parent=None, previous_section=None, next_section=None):
        super(TroubleSection, self).__init__()
        self._id = section_id
        self._level = level
        self._parent_id = parent
        self._previous_section_id = previous_section
        self._next_section_id = next_section
        self._messages_to_user = []
        self._message_type = []
        self._choices = []
        self._solution_type = []
        self._solution_message = []
        # move PV stuff to EpicsTroubleSection
        # self.solution_pv = [[]]
        # self.solution_pv_value = [[]]
        # self.solution_pv_message = [[]]
        self._solution_section_id = []  # maybe redundant with self.next

    def add_message(self, message_text):
        self._messages_to_user.append(message_text)
        if os.path.isfile(message_text):
            self._message_type.append(IMAGE)
        else:
            self._message_type.append(TEXT)

    def get_message(self, ind):
        return self._messages_to_user[ind]

    def get_message_type(self, ind):
        return self._message_type[ind]

    def add_choice(self, choice, **kwargs):
        self._choices.append(choice)
        solution_type = kwargs['solution_type']
        self._solution_type.append(solution_type)
        if solution_type == 'message':
            self._solution_message.append(kwargs['solution'])
            self._solution_section_id.append(None)
            return True
        elif solution_type == 'section':
            self._solution_message.append("Next")
            self._solution_section_id.append(kwargs['solution'])
            return True
        else:
            return False

    def get_choice(self, ind):
        return self._choices[ind]

    def get_solution_type(self, ind):
        return self._solution_type[ind]

    def get_solution_message(self, ind):
        return self._solution_message[ind]

    def get_solution_section_id(self, ind):
        return self._solution_section_id[ind]

    @property
    def message_counter(self):
        return len(self._messages_to_user)

    @property
    def choice_counter(self):
        return len(self._choices)

    @property
    def id(self):
        return self._id

    @property
    def parent_id(self):
        return self._parent_id

    @property
    def level(self):
        return self._level
