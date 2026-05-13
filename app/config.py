import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR    = Path(__file__).parent.parent
DATA_DIR    = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
ASSETS_DIR  = BASE_DIR / "assets"

DATA_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)

DB_PATH     = DATA_DIR / "teachcrm.db"
DB_VERSION  = 1

SUPABASE_URL      = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY      = os.getenv("SUPABASE_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

APP_NAME    = "OmniClass"
APP_VERSION = "0.1.0"

DEPED_PASSING_GRADE = 75.0
DEPED_HONORS_GRADE  = 90.0

WW_WEIGHT = 0.40
PT_WEIGHT = 0.40
QA_WEIGHT = 0.20

TERMS    = ["T1", "T2", "T3"]
QUARTERS = ["Q1", "Q2", "Q3", "Q4"]