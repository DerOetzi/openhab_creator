from __future__ import annotations

from openhab_creator.models.configuration.location.indoor import Indoor, IndoorType


@IndoorType()
class Room(Indoor):

    @property
    def typed(self) -> str:
        return 'Room'


class RoomType(IndoorType):
    pass


@RoomType()
class Bathroom(Room):
    pass


@RoomType()
class Bedroom(Room):
    pass


@RoomType()
class BoilerRoom(Room):
    pass


@RoomType()
class Cellar(Room):
    pass


@RoomType()
class DiningRoom(Room):
    pass


@RoomType()
class Entry(Room):
    pass


@RoomType()
class FamilyRoom(Room):
    pass


@RoomType()
class GuestRoom(Room):
    pass


@RoomType()
class Kitchen(Room):
    pass


@RoomType()
class LaundryRoom(Room):
    pass


@RoomType()
class LivingRoom(Room):
    pass


@RoomType()
class Office(Room):
    pass


@RoomType()
class Veranda(Room):
    pass
