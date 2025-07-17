import os
from platformdirs import user_data_dir

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
STORAGE_DIR = os.getenv("STORAGE_DIR", "VAULT")

APP_NAME = os.getenv("APP_NAME", "mycloudy")
APP_AUTHOR = os.getenv("APP_AUTHOR", "MyCloudyOrg")

VAULT_DIR = os.path.join(user_data_dir(APP_NAME, APP_AUTHOR), STORAGE_DIR)

correlationMap = {}