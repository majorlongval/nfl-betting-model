# nfl_betting_app/google_drive_handler.py
# This module handles authentication and file uploads/downloads to Google Drive.

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os

# The path to your client secrets file, located in the project root.
SECRETS_FILE = os.path.join(os.path.dirname(__file__), "..", "client_secrets.json")


def authenticate():
    """Handles the Google Drive authentication process using a command-line flow."""

    if not os.path.exists(SECRETS_FILE):
        raise FileNotFoundError(
            f"ERROR: The 'client_secrets.json' file was not found. "
            f"Please ensure it is located in the root directory of your project: "
            f"{os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))}"
        )

    auth_settings = {
        "client_config_file": SECRETS_FILE,
    }
    gauth = GoogleAuth(settings=auth_settings)

    creds_file = os.path.join(os.path.dirname(__file__), "..", "mycreds.txt")
    # Try to load saved credentials from the file
    gauth.LoadCredentialsFile(creds_file)

    if gauth.credentials is None:
        # --- MODIFIED AUTHENTICATION FLOW ---
        # Use CommandLineAuth() which is more robust than LocalWebserverAuth()
        # It will print a URL, you open it, authorize, and paste the code back.
        gauth.CommandLineAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()

    # Save the current credentials to a file for next time
    gauth.SaveCredentialsFile(creds_file)

    return GoogleDrive(gauth)


def upload_file_to_drive(local_file_path: str, drive_folder_id: str):
    """
    Uploads a local file to a specific folder in Google Drive. If the file
    already exists, it updates it.
    """
    try:
        print("Authenticating with Google Drive for upload...")
        drive = authenticate()
        print("Authentication successful.")

        file_name = os.path.basename(local_file_path)

        file_list = drive.ListFile({
            "q": f"'{drive_folder_id}' in parents and title='{file_name}' and trashed=false"
        }).GetList()

        if file_list:
            drive_file = file_list[0]
            print(f"Updating existing file '{file_name}' in Google Drive...")
            drive_file.SetContentFile(local_file_path)
            drive_file.Upload()
            print("File updated successfully.")
        else:
            print(f"Uploading new file '{file_name}' to Google Drive...")
            drive_file = drive.CreateFile({
                "title": file_name,
                "parents": [{"id": drive_folder_id}],
            })
            drive_file.SetContentFile(local_file_path)
            drive_file.Upload()
            print("File uploaded successfully.")

    except Exception as e:
        print(f"An error occurred during Google Drive upload: {e}")


def download_file_from_drive(
    drive_folder_id: str, file_name: str, local_save_path: str
) -> bool:
    """
    Downloads a file from a specific Google Drive folder to a local path.
    """
    try:
        print(f"Attempting to download '{file_name}' from Google Drive...")
        drive = authenticate()

        file_list = drive.ListFile({
            "q": f"'{drive_folder_id}' in parents and title='{file_name}' and trashed=false"
        }).GetList()

        if file_list:
            drive_file = file_list[0]
            print(f"File found. Downloading to '{local_save_path}'...")
            drive_file.GetContentFile(local_save_path)
            print("Download successful.")
            return True
        else:
            print("File not found in the specified Google Drive folder.")
            return False

    except Exception as e:
        print(f"An error occurred during Google Drive download: {e}")
        return False

