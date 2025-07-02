import importlib
from pathlib import Path

models_dir = Path(__file__).parent

for model_file in models_dir.glob("*.py"):
    if model_file.name != "__init__.py":
        module_name = f"{__name__}.{model_file.stem}"
        importlib.import_module(module_name)