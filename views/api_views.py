from email.policy import default
from flask import Blueprint, session, redirect, request, url_for, send_file, json, jsonify
import logging
import os

from module.img import *

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route("/getExif", methods=['POST'])
def getExif(): 
	if request.method == 'POST':
            try:
                  req_img = request.files["files"]
                  res = get_exif_data(req_img)
            except Exception as E:
                  res = None
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