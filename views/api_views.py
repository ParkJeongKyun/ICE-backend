from email.policy import default
from flask import Blueprint, session, redirect, request, url_for
import logging
import os

# 이미지 모듈
from module.img import *

# 블루프린터
bp = Blueprint('api', __name__, url_prefix='/api')

# EXIF 분석기
@bp.route("/getExif", methods=['POST'])
def getExif(): 
      if request.method == 'POST':
            try:
                  req_img = request.files["files"]
                  res = get_exif_data(req_img)
            except Exception as E:
                  res = None
                  logging.error(E)
            if(not res):
                  res = {
                        "EXIF": None,
                        'ImageWidth': None, 
                        'ImageLength': None,
                        'Make': None,
                        'Model': None,
                        'Software': None,
                        'DateTime': None,
                        'GPSInfo': None,
                        'ExifVersion': None,
                        'DateTimeOriginal': None,
                        'DateTimeDigitized': None,
                        'Flash': None,
                        'ImageUniqueID': None,
                  }
            return res