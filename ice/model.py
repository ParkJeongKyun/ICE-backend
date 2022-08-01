from pydantic import BaseModel
from fastapi import UploadFile
from typing import Optional, Tuple, List

# EXIF 데이터 모델
class ExifData(BaseModel):
    ImageWidth: Optional[int] = None
    ImageLength: Optional[int] = None
    Make: Optional[str] = None
    Model: Optional[str] = None
    Software: Optional[str] = None
    DateTime: Optional[str] = None
    GPSInfo: Tuple[float, float] = None
    ExifVersion: Optional[str] = None
    DateTimeOriginal: Optional[str] = None
    DateTimeDigitized: Optional[str] = None
    Flash: Optional[int] = None
    ImageUniqueID: Optional[str] = None

    class Config:
        orm_mode = True

# getExIF 응답용 모델
class GetExifResponse(BaseModel):
    EXIF: bool = False
    EXIF_DATA: Optional[ExifData] = None
