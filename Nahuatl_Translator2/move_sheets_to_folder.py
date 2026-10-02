#!/usr/bin/env python3
"""
move_sheets_to_folder.py — Move the 10 transcription sheets into the
target Drive folder, using user OAuth credentials (token.json).

Reads transcribe_progress.json for sheet IDs, then calls Drive API
files.update(addParents=TARGET_FOLDER_ID) for each.

Run on laptop:
  python3 move_sheets_to_folder.py
"""

import json
import os
import time

from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

_HERE = os.path.dirname(os.path.abspath(__file__))
PROGRESS_PATH = os.path.join(_HERE, 'transcribe_progress.json')
TARGET_FOLDER_ID = '1LW0qwgf58wUX1UhpL7K2Y_6gW5x_NAoF'

TOKEN_CANDIDATES = [
    os.path.expanduser('~/token.json'),
    '/home/wslinux/WS_Qwen_Projects_Windows/Financial_Analysis_App/python/token.json',
    '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json',
    os.path.join(_HERE, 'token.json'),
]


def load_user_creds():
    token_path = next((p for p in TOKEN_CANDIDATES if os.path.isfile(p)), None)
    if not token_path:
        raise FileNotFoundError('token.json not found in any candidate path')

    with open(token_path) as f:
        tok = json.load(f)

    creds = OAuthCredentials(
        token=tok.get('token'),
        refresh_token=tok.get('refresh_token'),
        token_uri=tok.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=tok.get('client_id'),
        client_secret=tok.get('client_secret'),
        scopes=tok.get('scopes'),
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        tok['token'] = creds.token
        tok['expiry'] = creds.expiry.isoformat() if creds.expiry else tok.get('expiry')
        with open(token_path, 'w') as f:
            json.dump(tok, f, indent=2)
        print('[auth] Token refreshed')

    print(f'[auth] User OAuth: {token_path}')
    return creds


def main():
    with open(PROGRESS_PATH) as f:
        progress = json.load(f)

    print(f'[load] {len(progress)} sheets to move\n')

    creds = load_user_creds()
    drive_svc = build('drive', 'v3', credentials=creds)

    for file_id, info in progress.items():
        sheet_id = info['sheet_id']
        label = info['label']
        print(f'Moving: {label}')
        try:
            drive_svc.files().update(
                fileId=sheet_id,
                addParents=TARGET_FOLDER_ID,
                removeParents='root',
                fields='id, parents',
            ).execute()
            print(f'  OK — https://docs.google.com/spreadsheets/d/{sheet_id}/edit')
        except Exception as e:
            print(f'  ERROR: {e}')
        time.sleep(0.5)

    print('\nDone.')


if __name__ == '__main__':
    main()
