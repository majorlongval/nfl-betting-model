import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

GDRIVE_FOLDER_ID = "1Z5qgcNC87J-lpsCeB0Zy3ndYUfbwDPqj"

GAMES_DB_FILENAME = "nfl_games_database.csv"
LOCAL_GAMES_DB_PATH = os.path.join(DATA_DIR, GAMES_DB_FILENAME)

STATS_DB_FILENAME = "nfl_team_stats.csv"
LOCAL_STATS_DB_PATH = os.path.join(DATA_DIR, STATS_DB_FILENAME)

START_YEAR = 2006
