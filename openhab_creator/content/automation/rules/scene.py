# pylint: skip-file
from core.log import LOG_PREFIX, logging
from core.rules import rule
from core.triggers import when
from personal.item import Group
from personal.scenemanager import SceneManager
import personal.scenemanager
reload(personal.scenemanager)

manager = SceneManager.instance()


@rule('Scenes start up')
@when('System started')
@when('Member of sceneTimeConfiguration received command')
def scene_startup(event):
    if event is None:
        for auto_item in Group('AutoLight'):
            reactivation_item = auto_item.from_scripting('reactivation_item')
            reactivation_period = reactivation_item.get_int(0, True)
            if reactivation_period > 0:
                auto_item.post_update(ON)

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
@when('Item darkness changed')
@when('Member of Lightcontrol received command')
def activate_scene(event):
    manager.activate_scene(event)


def scriptUnloaded():  # NOSONAR
    manager.clear_timer()
