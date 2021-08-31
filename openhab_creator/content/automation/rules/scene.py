# pylint: skip-file
from core.log import LOG_PREFIX, logging
from core.rules import rule
from core.triggers import when
from personal.scenemanager import SceneManager
import personal.scenemanager
reload(personal.scenemanager)

manager = SceneManager.instance()


@rule('Scenes start up')
@when('System started')
@when('Member of sceneTimeConfiguration received command')
def scene_startup(event):
    manager.read_timeconfig(event)
    manager.start_scene_timer()
    manager.change_scene()


@rule('Change scene')
@when('Item autoScene received command ON')
@when('Item autoSceneActive received command')
@when('Item autoGuestStayed received command')
@when('Descendent of Presences changed')
@when('Item wayhome received command')
def change_scene(event):
    manager.change_scene(event)


@rule('Activate scene')
@when('Descendent of Auto received command')
@when('Member of Lightcontrol received command')
@when('Item darkness changed')
def activate_scene(event):
    manager.activate_scene(event)


def scriptUnloaded():  # NOSONAR
    manager.clear_timer()
