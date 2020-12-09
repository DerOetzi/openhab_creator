import csv

class SecretsRegistry(object):
    SECRETS_REGISTRY = {}

    MISSING_KEYS = []

    @staticmethod
    def init(secretsfile):
        reader = csv.DictReader(secretsfile)

        for row in reader:
            if row['value'].strip() == '':
                print("Empty secret: %s" % row['key'])
                SecretsRegistry.SECRETS_REGISTRY[row['key'].lower()] = '__%s__' % (row['key'].upper())
            else:
                SecretsRegistry.SECRETS_REGISTRY[row['key'].lower()] = row['value'].strip()
        pass

    @staticmethod
    def secret(*args):
        key = '_'.join(args).lower()

        if key in SecretsRegistry.SECRETS_REGISTRY:
            return SecretsRegistry.SECRETS_REGISTRY[key]
        else:
            if key not in SecretsRegistry.MISSING_KEYS:
                SecretsRegistry.MISSING_KEYS.append(key)
            return "__%s__" % key.upper()

    @staticmethod
    def hasMissing():
        return len(SecretsRegistry.MISSING_KEYS) > 0

    @staticmethod
    def handleMissing():
        if SecretsRegistry.hasMissing():
            print("Missing secrets:")
            for key in SecretsRegistry.MISSING_KEYS:
                print(key)