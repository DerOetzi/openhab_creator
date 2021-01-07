from openhab_creator.models.formatter import Formatter

class BaseObject(object):
    _id: str
    _name: str
    _typed: str
    _icon: str

    def __init__(self, name: str, configuration: dict, validtypes: list, id: str = None):
        if id is None:
            id = configuration.get('id', None)
            if id is None:
                id = Formatter.formatId(name)

        self._id = Formatter.ucfirst(id)

        self._name = name

        typed = configuration.get('type', None)
        if typed is None:
            self._typed = validtypes[0]
        else:
            typed = typed.lower()
            if typed in validtypes:
                self._typed = typed
            else:
                raise Exception('Invalid type {} for {}'.format(typed, name))

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
        return f'{self._name} ({self.id}, {self._typed})'
