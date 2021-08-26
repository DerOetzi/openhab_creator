# pylint: skip-file
from core.log import LOG_PREFIX, logging
from core.rules import rule
from core.triggers import when
from personal.scenemanager import SceneManager


@rule('Scenes start up')
@when('System started')
@when('Member of sceneTimeConfiguration received command')
def scene_startup(event):
    manager = SceneManager.instance()
    manager.read_timeconfig(event)
    manager.start_scene_timer()
    manager.change_scene()


def scriptUnloaded():  # NOSONAR
    manager = SceneManager.instance()
    manager.clear_timer()
