# google_drive/utils.py
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from .models import GoogleDriveToken


def get_credentials_from_token(token_record):
    try:
        creds = Credentials(
            token=token_record.access_token,
            refresh_token=token_record.refresh_token,
            token_uri=token_record.token_uri,
            client_id=token_record.client_id,
            client_secret=token_record.client_secret,
            scopes=token_record.scopes.split(',')
        )
        # Only refresh if expired AND we have a refresh token
        # Do NOT always force-refresh — causes invalid_scope on old tokens
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_record.access_token = creds.token
            token_record.save()
        return creds
    except Exception as e:
        print(f"Error in get_credentials_from_token: {e}")
        return None


def get_user_drive_credentials(user):
    """
    Returns Google credentials for the given user.
    Falls back to the system's shared drive token if the user is flagged to use it.
    """
    if not user or not user.is_authenticated:
        return None

    try:
        # 1. Check for a personal token for this specific user
        token_record = GoogleDriveToken.objects.filter(user=user).first()

        # 2. Fallback for predefined shared accounts
        if not token_record and hasattr(user, 'admin_profile'):
            if user.admin_profile.use_shared_google_drive:
                token_record = GoogleDriveToken.objects.first()

        if not token_record:
            return None

        return get_credentials_from_token(token_record)

    except Exception as e:
        print(f"Error in get_user_drive_credentials: {e}")
        return None