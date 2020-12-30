import os

from .bridge import BridgeFactory

class ItemsCreator(object):
    def __init__(self, outputdir):
        self._outputdir = '%s/items' % outputdir

    def buildLocations(self, floors, checkOnly = False):
        lines = []
        for floor in floors:
            lines.append(floor.floorstring())
            for room in floor.rooms():
                lines.append(room.roomstring())

        if not checkOnly:
            self._writeFile('locations', lines)

    def _writeFile(self, itemsfile, lines):
        if not os.path.exists(self._outputdir):
            os.makedirs(self._outputdir)

        with open('%s/%s.items' % (self._outputdir, itemsfile), 'w') as f:
            f.writelines("\n".join(lines))