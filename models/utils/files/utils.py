import uuid
from datetime import datetime

def create_unique_filename(file):
    extension = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4().hex}_{int(datetime.timestamp(datetime.now()))}.{extension}"
    file_name = file.filename

    file_metadata = {
        "file_name": file_name,
        "unique_filename": unique_filename,
        "file_extension": extension
    }
    return file_metadata



