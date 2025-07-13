import os

SECRET_KEY = os.getenv("SECRET_KEY")
FINAL_DIR = os.getenv("FINAL_DIR", "MYCLOUDY_VAULT")

correlationMap = {}