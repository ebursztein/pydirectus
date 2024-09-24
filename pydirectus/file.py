from pathlib import Path
from typing import Optional, Union
from datetime import datetime, timezone
from .typing import Uuid
from .session import Session

class File:
    "Directus file metadata and  method"
    id: Uuid  # Primary key of the file (UUID)
    storage: str  # Storage adapter used for the file (e.g., "local")
    filename_disk: str  # Name of the file as saved on the storage adapter
    filename_download: str  # Preferred filename when the file is downloaded
    title: str  # Title for the file
    type: str  # Mimetype of the file (e.g., "image/jpeg")
    folder: Optional[str] = None  # ID of the folder the file is in (many-to-one to folders)
    created_on: datetime  # When the file was created
    uploaded_by: Optional[str] = None  # ID of the user who uploaded the file (many-to-one to users)
    uploaded_on: datetime  # When the file was last uploaded/replaced
    modified_by: Optional[str] = None  # ID of the user who last modified the file (many-to-one to users)
    modified_on: Optional[datetime] = None  # When the file was last modified
    filesize: int  # Size of the file in bytes
    width: Optional[int] = None  # Width of the image/video in pixels (if applicable)
    height: Optional[int] = None  # Height of the image/video in pixels (if applicable)
    focal_point_x: Optional[float] = None  # X-coordinate of the focal point for image cropping (if applicable)
    focal_point_y: Optional[float] = None  # Y-coordinate of the focal point for image cropping (if applicable)
    duration: Optional[int] = None  # Duration of audio/video in milliseconds (if applicable)
    description: Optional[str] = None  # Description of the file
    location: Optional[str] = None  # Location of the file
    tags: Optional[list[str]] = None  # Tags associated with the file
    metadata: Optional[dict] = None  # Additional metadata (e.g., Exif, IPTC, ICC for images)

    def __init__(self, json_data: dict, session: Session) -> None:
        self._session = session
        self.id = str(json_data["id"])
        self.storage = str(json_data["storage"])
        self.filename_disk = str(json_data["filename_disk"])
        self.filename_download = str(json_data["filename_download"])
        self.title = str(json_data["title"])
        self.type = str(json_data["type"])
        self.folder = str(json_data.get("folder")) if json_data.get("folder") is not None else None
        self.created_on = self._parse_datetime(json_data["created_on"])
        self.uploaded_by = str(json_data.get("uploaded_by")) if json_data.get("uploaded_by") is not None else None
        self.uploaded_on = self._parse_datetime(json_data["uploaded_on"])
        self.modified_by = str(json_data.get("modified_by")) if json_data.get("modified_by") is not None else None
        self.modified_on = self._parse_datetime(json_data.get("modified_on"))
        self.filesize = int(json_data["filesize"])
        self.width = int(json_data.get("width")) if json_data.get("width") is not None else None
        self.height = int(json_data.get("height")) if json_data.get("height") is not None else None
        self.focal_point_x = float(json_data.get("focal_point_x")) if json_data.get("focal_point_x") is not None else None
        self.focal_point_y = float(json_data.get("focal_point_y")) if json_data.get("focal_point_y") is not None else None
        self.duration = int(json_data.get("duration")) if json_data.get("duration") is not None else None
        self.description = str(json_data.get("description")) if json_data.get("description") is not None else None
        self.location = str(json_data.get("location")) if json_data.get("location") is not None else None
        self.tags = list(json_data.get("tags")) if json_data.get("tags") is not None else None
        self.metadata = dict(json_data.get("metadata")) if json_data.get("metadata") is not None else None

        if self.filesize >= 1048576:  # 1 MB
            self.pretty_filesize = f"{self.filesize//1048576} MB"
        else:
            self.pretty_filesize = f"{self.filesize//1024} KB"

    @staticmethod
    def _parse_datetime(datetime_str: Optional[str]) -> Optional[datetime]:
        if datetime_str:
            if datetime_str.endswith("Z"):
                return datetime.fromisoformat(datetime_str[:-1]).replace(tzinfo=timezone.utc)  # Remove "Z" and set UTC timezone
            else:
                return datetime.fromisoformat(datetime_str)
        else:
            return None

    def __repr__(self) -> str:
        return f"<File {self.filename_download} ({self.pretty_filesize})>"
