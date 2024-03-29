from PIL import Image
import logging
from typing import Optional, Tuple
from model import ExifData

# 필터 리스트
SELECT_LIST = {
    256: 'ImageWidth', # 이미지 너비
    257: 'ImageLength', # 이미지 길이/높이
    271: 'Make', # 제조사
    272: 'Model', # 모델
    305: 'Software', # 프로그램명
    306: 'DateTime', # 날짜
    34853: 'GPSInfo', # 위치정보
    36864: 'ExifVersion', # Exif 버전 
    36867: 'DateTimeOriginal', # 원본촬영시간
    36868: 'DateTimeDigitized', # 디지털화된시간
    37385: 'Flash', # 플래시
    42016: 'ImageUniqueID' # 이미지 ID
}

# EXIF 데이터 얻기
def get_exif_data(img_path) -> Optional[ExifData]:
    try:
        img = Image.open(img_path)
        exif_data = img._getexif()
        img.close()
    except Exception as E: # 이미지를 불러올 수 없는 경우
        exif_data = None
        logging.error(E)
    if exif_data is None: # EXIF 데이터가 없는 경우 N
        return None
    if exif_data is not None: # EXIF 데이터가 있는 경우
        taglabel = {}
        for id in SELECT_LIST :
            if id in exif_data.keys():
                val = exif_data[id]
                if val is not None: # 값이 비어 있지만 않은 경우(0도 가능)
                    if id == 34853: # GPS 위치 정보
                        val = get_gps_data(exif_data[id])
                    elif id == 36864: # EXIF 버전
                        try :
                            val = exif_data[id].decode("utf-8")
                        except:
                            val = exif_data[id]
                    elif id in (306, 36867, 36868): # 시간 정보 포메팅 
                        tmp = exif_data[id].split()
                        val = "{0} {1}".format(tmp[0].replace(":", "-"), tmp[1])
                    else:
                        val = exif_data[id]
                else:
                    val = None
            else:
                val = None # 해당 태그 정보가 없는 경우
            taglabel[SELECT_LIST[id]] = val
        return taglabel

# GPS 데이터 얻기
def get_gps_data(exifGPS) -> Optional[Tuple[float, float]]:
    try: 
        latData = exifGPS[2]
        lonData = exifGPS[4]
        # 도, 분, 초 계산
        try: # 계산되어 있지 않는 경우
            latDeg = latData[0][0] / float(latData[0][1])
            latMin = latData[1][0] / float(latData[1][1])
            latSec = latData[2][0] / float(latData[2][1])
            lonDeg = lonData[0][0] / float(lonData[0][1])
            lonMin = lonData[1][0] / float(lonData[1][1])
            lonSec = lonData[2][0] / float(lonData[2][1])
        except: # 계산된 경우
            latDeg = latData[0]
            latMin = latData[1]
            latSec = latData[2]
            lonDeg = lonData[0]
            lonMin = lonData[1]
            lonSec = lonData[2]
        # 도, 분, 초로 나타내기
        #Lat = str(int(latDeg)) + "°" + str(int(latMin)) + "'" + str(latSec) + "\"" + exifGPS[1]
        #Lon = str(int(lonDeg)) + "°" + str(int(lonMin)) + "'" + str(lonSec) + "\"" + exifGPS[3]
        # 위도 계산
        Lat = (latDeg + (latMin + latSec / 60.0) / 60.0)
        # 북위, 남위인지를 판단, 남위일 경우 -로 변경
        if exifGPS[1] == 'S': Lat = Lat * -1
        # 경도 계산
        Lon = (lonDeg + (lonMin + lonSec / 60.0) / 60.0)
        # 동경, 서경인지를 판단, 서경일 경우 -로 변경
        if exifGPS[3] == 'W': Lon = Lon * -1
        return (Lat, Lon)
    except Exception as E:
        logging.error(E)
        return None