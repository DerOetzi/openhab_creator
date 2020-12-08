class SecretRegistry(object):
    SECRET_REGISTRY = []

    @staticmethod
    def secret(*args):
        # TODO Read secrets file to registry and check for key and return value
        key = '_'.join(args)

        return "__%s__" % key.upper()