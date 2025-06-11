from nfl_betting_app.google_drive_handler import (
    download_file_from_drive,
    upload_file_to_drive,
)
from nfl_betting_app.data_retriever import update_local_game_data
import nfl_betting_app.config as config


def main():
    print("--- Starting Weekly NFL Betting Pipeline ---")

    print("\n[Step 1/4] Downloading latest database from GoogleDrive...")
    download_file_from_drive(
        drive_folder_id=config.GDRIVE_FOLDER_ID,
        file_name=config.GAMES_DB_FILENAME,
        local_save_path=config.LOCAL_GAMES_DB_PATH,
    )

    print("\n[Step 2/4] Checking for and retrieving new game data")
    update_local_game_data(start_year=config.START_YEAR)

    print("Local data is now up-to-date.")

    print("\n[Step 3/4] Running prediction model and generating bets...")
    print("... bets for the week would be generated here")

    print("\n[Step 4/4] Uploading updated database back to Google Drive")
    upload_file_to_drive(
        local_file_path=config.LOCAL_GAMES_DB_PATH,
        drive_folder_id=config.GDRIVE_FOLDER_ID,
    )

    print("\n--- Pipeline Run Complete ---")


if __name__ == "__main__":
    main()
