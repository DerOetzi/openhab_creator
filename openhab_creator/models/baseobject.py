from openhab_creator.exception import ConfigurationException

from openhab_creator.models.formatter import Formatter

class BaseObject(object):
    _id: str
    _name: str
    _typed: str
    _icon: str

    def __init__(self, name: str, configuration: dict, validtypes: list, id: str = None):
        if id is None:
            self._id = configuration.get('id', None)
            if self._id is None:
                self._id = Formatter.format_id(name)
        else:
            self._id = id

        self._id = Formatter.ucfirst(self._id)

        self._name = name

        typed = configuration.get('type', None)
        if typed is None:
            self._typed = validtypes[0]
        else:
            typed = typed.lower()
            if typed in validtypes:
                self._typed = typed
            else:
                raise ConfigurationException('Invalid type {} for {}'.format(typed, name))

        self._icon = configuration.get('icon', None)
        if self._icon is None:
            self._icon = self._typed

    def id(self) -> str:
        return self._id

    def name(self) -> str:
        return self._name

    def typed(self) -> str:
        return self._typed

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'{self._name} ({self._id}, {self._typed})'
