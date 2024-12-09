import os
import zipfile
from datetime import datetime, timedelta
from django.conf import settings
# utils.py
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

def archive_and_delete_old_media_files(output_filename="old_media_archive.zip"):
    """
    Archive files in the media directory older than 3 years and delete them.
    """
    three_years_ago = datetime.now() - timedelta(days=3 * 365)
    media_path = settings.MEDIA_ROOT
    archive_dir = os.path.join(settings.MEDIA_ROOT, 'archives')
    os.makedirs(archive_dir, exist_ok=True)
    archive_path = os.path.join(archive_dir, output_filename)

    with zipfile.ZipFile(archive_path, 'w') as archive:
        for root, dirs, files in os.walk(media_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

                # Archive and delete files older than 3 years
                if file_mtime < three_years_ago:
                    archive.write(file_path, os.path.relpath(file_path, media_path))
                    os.remove(file_path)  # Delete the file after archiving

    return archive_path


def generate_signed_url(base_url, data, expiration=300):
    """
    Generate a signed URL that expires after a certain time.
    
    Args:
        base_url (str): The base URL to append the token to.
        data (str): The data to sign (e.g., user ID, or any identifier).
        expiration (int): Expiration time in seconds (default: 5 minutes).
    
    Returns:
        str: The signed URL.
    """
    signer = TimestampSigner()
    signed_data = signer.sign(data)
    return f"{base_url}?token={signed_data}"

def validate_signed_token(token, max_age=300):
    """
    Validate a signed token and check if it's expired.
    
    Args:
        token (str): The signed token to validate.
        max_age (int): Maximum age of the token in seconds.
    
    Returns:
        str: The original data if valid.
    
    Raises:
        SignatureExpired: If the token has expired.
        BadSignature: If the token is invalid.
    """
    signer = TimestampSigner()
    try:
        return signer.unsign(token, max_age=max_age)
    except SignatureExpired:
        raise SignatureExpired("The Link has expired.")
    except BadSignature:
        raise BadSignature("The token is invalid.")
