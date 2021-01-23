from __future__ import annotations

from openhab_creator.output.content.basecontentcreator import BaseContentCreator


class JSR223Creator(BaseContentCreator):
    BASESRCPATH = 'automation/helper/Core/automation/'

    def build(self):
        self._copy_all_files_from_subdir(
            f'{self.BASESRCPATH}lib/python/core', '/automation/lib/python/core')

        self._copy_all_files_from_subdir(
            f'{self.BASESRCPATH}jsr223/python/core', '/automation/jsr223/core')
