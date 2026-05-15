from django.core.management.base import BaseCommand
from google_drive.models import GoogleDriveToken
from google_drive.utils import get_credentials_from_token

class Command(BaseCommand):
    help = 'Diagnostic tool to check if any valid Google Drive tokens exist in the system.'

    def handle(self, *args, **options):
        tokens = GoogleDriveToken.objects.all()
        
        if not tokens.exists():
            self.stdout.write(self.style.ERROR(
                "CRITICAL: No Google Drive tokens found in the database. "
                "The shared drive fallback will not work until an admin connects their account."
            ))
            return

        self.stdout.write(self.style.SUCCESS(f"Found {tokens.count()} token(s). Checking validity..."))

        for t in tokens:
            creds = get_credentials_from_token(t)
            if creds and creds.valid:
                status = self.style.SUCCESS("VALID")
                user_info = f"User: {t.user.username}"
            else:
                status = self.style.ERROR("INVALID/EXPIRED")
                user_info = f"User: {t.user.username}"
            
            self.stdout.write(f"  - [{status}] {user_info}")