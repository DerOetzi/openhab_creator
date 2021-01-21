from __future__ import annotations

import csv
import os
from typing import Dict, List


class SecretsRegistry(object):
    SECRETS_REGISTRY: Dict[str, str] = {}

    MISSING_KEYS: List[str] = []

    @staticmethod
    def init(configdir: str) -> None:
        with open(os.path.join(configdir, 'secrets.csv')) as secretsfile:
            reader = csv.DictReader(secretsfile)

            for row in reader:
                if row['value'].strip() == '':
                    print("Empty secret: %s" % row['key'])
                    SecretsRegistry.SECRETS_REGISTRY[row['key'].lower()] = '__%s__' % (
                        row['key'].upper())
                else:
                    SecretsRegistry.SECRETS_REGISTRY[row['key'].lower(
                    )] = row['value'].strip()

    @staticmethod
    def secret(*args: List[str]) -> str:
        key = '_'.join(args).lower()

        if key in SecretsRegistry.SECRETS_REGISTRY:
            return SecretsRegistry.SECRETS_REGISTRY[key]
        else:
            if key not in SecretsRegistry.MISSING_KEYS:
                SecretsRegistry.MISSING_KEYS.append(key)
            return "__%s__" % key.upper()

    @staticmethod
    def has_missing() -> bool:
        return len(SecretsRegistry.MISSING_KEYS) > 0

    @staticmethod
    def handle_missing() -> None:
        if SecretsRegistry.has_missing():
            print("Missing secrets:")
            for key in SecretsRegistry.MISSING_KEYS:
                print(key)
