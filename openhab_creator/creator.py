from . import __version__

import json

class Creator(object):
    def __init__(self, configfile):
        self.configjson = json.load(configfile)
        print(self.configjson)

def run(configfile, outputdir):
    print("openHAB Configuration Creator (%s)" % __version__)
    print("Output directory: %s" % outputdir)

    creator = Creator(configfile)
