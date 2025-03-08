import os
import importlib
from pathlib import Path

# Get the directory of this file
models_dir = Path(__file__).parent

# Dynamically import all .py files inside models/
for model_file in models_dir.glob("*.py"):
    if model_file.name != "__init__.py":
        module_name = f"{__name__}.{model_file.stem}"  # Keep the full package path
        importlib.import_module(module_name)