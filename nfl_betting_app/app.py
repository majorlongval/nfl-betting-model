# nfl_betting_app/app.py
# The main orchestrator for the NFL betting application.

# Import our custom application modules
from nfl_betting_app.google_drive_handler import (
    download_file_from_drive,
    upload_file_to_drive,
)
from nfl_betting_app.data_retriever import update_raw_pbp_data
from nfl_betting_app.data_handler import load_raw_pbp_data
from nfl_betting_app.feature_engineering import create_final_feature_set
import nfl_betting_app.config as config # I noticed this was create_point_in_time_features, but the file has create_final_feature_set
import os


def run_data_pipeline():
    """
    Handles the complete data engineering workflow:
    1. Syncs raw data FROM Google Drive.
    2. Updates raw data FROM the web.
    3. Generates processed feature set FROM raw data.
    4. Syncs ALL updated data TO Google Drive.
    """
    print("--- Running Full Data Pipeline ---")

    # === STEP 1: Sync RAW Data from Google Drive ===
    print("\n[Step 1/4] Syncing RAW data from Google Drive...")
    if config.GDRIVE_RAW_DATA_FOLDER_ID != "YOUR_RAW_DATA_FOLDER_ID_HERE":
        # Download the raw PBP DB
        download_file_from_drive(
            drive_folder_id=config.GDRIVE_RAW_DATA_FOLDER_ID,
            file_name=config.RAW_PBP_DB_FILENAME,
            local_save_path=config.RAW_PBP_DB_PATH,
        )
    else:
        print(
            "WARNING: Google Drive Folder ID for raw data not set. Skipping download."
        )

    # === STEP 2: Update RAW Data from Web ===
    print("\n[Step 2/4] Updating local RAW data files from the web...")
    update_raw_pbp_data()

    # === STEP 3: Generate PROCESSED Features ===
    print("\n[Step 3/4] Generating PROCESSED features...")
    try:
        # The PBP data is now the single source of truth for game and play information.
        pbp_df = load_raw_pbp_data()

        feature_df = create_final_feature_set(pbp_df)

        os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
        feature_df.to_csv(config.MODEL_FEATURE_SET_PATH, index=False)
        print(
            f"Processed feature set saved locally to: {config.MODEL_FEATURE_SET_PATH}"
        )

    except FileNotFoundError as e:
        print(
            f"ERROR: A raw data file was not found. Cannot generate features. Details: {e}"
        )
        return  # Stop if we can't generate features

    # === STEP 4: Sync ALL Data back to Google Drive ===
    print("\n[Step 4/4] Uploading all updated data back to Google Drive...")
    # Upload raw files
    if config.GDRIVE_RAW_DATA_FOLDER_ID != "YOUR_RAW_DATA_FOLDER_ID_HERE":
        upload_file_to_drive(config.RAW_PBP_DB_PATH, config.GDRIVE_RAW_DATA_FOLDER_ID)
    else:
        print("WARNING: Raw data Google Drive ID not set. Skipping raw file upload.")

    # Upload processed file
    if config.GDRIVE_PROCESSED_DATA_FOLDER_ID != "YOUR_PROCESSED_DATA_FOLDER_ID_HERE":
        upload_file_to_drive(
            config.MODEL_FEATURE_SET_PATH, config.GDRIVE_PROCESSED_DATA_FOLDER_ID
        )
    else:
        print(
            "WARNING: Processed data Google Drive ID not set. Skipping feature file upload."
        )

    print("\n--- Data Pipeline Complete ---")


def main():
    """
    Main entry point for the application.
    """
    # Run the data engineering pipeline first
    run_data_pipeline()

    # Placeholder for the modeling and betting simulation part of the app
    print("\n--- Starting Prediction and Strategy Phase --- (Placeholder)")
    # predictor = Predictor(config.BEST_MODEL_PARAMS)
    # predictor.train(load_processed_data())
    # weekly_bets = predictor.generate_bets_for_week(season, week)
    # print(weekly_bets)
    print("...prediction and betting logic would run here...")
    print("\n--- Application Run Finished ---")


if __name__ == "__main__":
    main()
