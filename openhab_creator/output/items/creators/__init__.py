import os
from importlib import import_module
from inspect import isclass
from pathlib import Path
from pkgutil import iter_modules

package_dir = Path(__file__).resolve().parent
for (_, module_name, _) in iter_modules([os.fsdecode(package_dir)]):
    module = import_module(f"{__name__}.{module_name}")
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)

        if isclass(attribute):
            globals()[attribute_name] = attribute
