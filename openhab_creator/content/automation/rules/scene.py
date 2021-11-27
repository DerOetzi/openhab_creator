# pylint: skip-file
import personal.scenemanager
from core.log import LOG_PREFIX, logging
from core.rules import rule
from core.triggers import when

from personal.item import Group
from personal.scenemanager import SceneManager
from personal.autoitemmanager import AutoItemManager

reload(personal.scenemanager)

manager = SceneManager.instance()


@rule('Scenes start up')
@when('System started')
@when('Member of sceneTimeConfiguration received command')
def scene_startup(event):
    if event is None:
        AutoItemManager.startup()

    manager.read_timeconfig(event)
    manager.start_scene_timer()
    manager.change_scene()


@rule('Change scene')
@when('Item autoScene received command ON')
@when('Item autoSceneActive received command')
@when('Item autoGuestStayed received command')
@when('Descendent of Presences changed')
@when('Item wayhome received command ON')
def change_scene(event):
    manager.change_scene(event)


@rule('Activate scene')
@when('Item darkness changed')
@when('Item heating changed')
@when('Descendent of Auto received command')
def activate_scene(event):
    manager.activate_scene(event)


def scriptUnloaded():  # NOSONAR
    manager.clear_timer()
