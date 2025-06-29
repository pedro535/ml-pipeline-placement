import sys
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from dateutil import tz
from loguru import logger

load_dotenv()

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
KUBE_CONFIG = os.getenv("KUBE_CONFIG")
KFP_URL = os.getenv("KFP_URL")
KFP_API_ENDPOINT = os.getenv("KFP_API_ENDPOINT", "/pipeline/apis/v2beta1")
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL")
ENABLE_CACHING = os.getenv("ENABLE_CACHING", "false").lower() == "true"
PIPELINES_DIR = os.getenv("PIPELINES_DIR", "./pipelines")
WAIT_INTERVAL = int(os.getenv("WAIT_INTERVAL", "10"))
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "5"))
NODE_EXPORTER_PORT = int(os.getenv("NODE_EXPORTER_PORT", "9100"))
KUBE_APISERVER_PORT = int(os.getenv("KUBE_APISERVER_PORT", "10250"))
PIPELINE_FILENAME = "pipeline.py"
KFP_PREFIX = "kfp_"
METADATA_FILENAME = "metadata.json"
DATASETS_PATH = os.getenv("DATASETS_PATH")
EPOCH_DATE = datetime.fromtimestamp(0, tz=tz.tzutc())
PLACER = os.getenv("PLACER")
SEED = int(os.getenv("SEED", "42"))
N_PIPELINES_CSV = os.getenv("N_PIPELINES_CSV")

pipelines_dir = Path(PIPELINES_DIR).resolve()
pipelines_dir.mkdir(parents=True, exist_ok=True)

# Configure logger
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>  <cyan>{level}</cyan>  {message}",
    level="INFO"
)