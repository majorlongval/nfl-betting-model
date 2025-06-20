import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

GDRIVE_RAW_DATA_FOLDER_ID = "1T856I1m0_EsNkgT_kyo5WF_CX6RUHt87"
GDRIVE_PROCESSED_DATA_FOLDER_ID = "1EJihhAxpEOHDpF6l3AmsUAjgi_VW1EU_"

RAW_GAMES_DB_FILENAME = "nfl_games_database_raw.csv"
RAW_GAMES_DB_PATH = os.path.join(RAW_DATA_DIR, RAW_GAMES_DB_FILENAME)

RAW_STATS_DB_FILENAME = "nfl_weekly_player_stats_raw.csv"
RAW_STATS_DB_PATH = os.path.join(RAW_DATA_DIR, RAW_STATS_DB_FILENAME)

MODEL_FEATURE_SET_PATH = os.path.join(PROCESSED_DATA_DIR, "nfl_model_features.csv")

START_YEAR = 2007
