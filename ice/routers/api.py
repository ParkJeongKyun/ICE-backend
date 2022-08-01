from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
import io
import json
import logging

from model import GetExifResponse, ExifData
from module import get, edit

# 라우터
router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)

# EXIF 분석
@router.post("/getExif", response_model=GetExifResponse)
async def getExif(upload_img: UploadFile):
    try:
        res = GetExifResponse()
        request_object_content = await upload_img.read()
        exifData = get.get_exif_data(io.BytesIO(request_object_content))
        if exifData: # EXIF가 있는 경우
            res.EXIF = True
            res.EXIF_DATA = ExifData(**exifData)
    except Exception as E:
        logging.error(E)
        res = None
    finally:
        return res

# EXIF 수정
@router.post("/editExif")
async def editExif(chList: str = Form(...), upload_img: UploadFile = File(...)):
    try:
        request_object_content = await upload_img.read()
        chList = ExifData(**json.loads(chList))
        edited_img = edit.edit_exif_data(io.BytesIO(request_object_content), chList.dict())
        if edited_img:
            res = StreamingResponse(edited_img, media_type="image/jpeg")
        else:
            res = None
    except Exception as E:
        logging.error(E)
        res = None
    finally:
        return res