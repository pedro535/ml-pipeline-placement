import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
KUBE_CONFIG = os.getenv("KUBE_CONFIG", "/root/.kube/config")
KFP_URL = os.getenv("KFP_URL", "default_url")
ENABLE_CACHING = os.getenv("ENABLE_CACHING", "false").lower() == "true"
PIPELINES_DIR = os.getenv("PIPELINES_DIR", "./pipelines")
WAIT_INTERVAL = int(os.getenv("WAIT_INTERVAL", "10"))
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "30"))

pipelines_dir = Path(PIPELINES_DIR).resolve()
pipelines_dir.mkdir(parents=True, exist_ok=True)
