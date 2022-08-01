from PIL import Image
import logging
from io import BytesIO
from typing import Optional, Iterable

# 수정할 필터 리스트
SELECT_LIST_FOR_EDIT = {
    'data' : { #_data 안에 있는 정보들
        'ImageWidth': 256, # 이미지 너비
        'ImageLength': 257, # 이미지 길이/높이
        'Make': 271, # 제조사
        'Model': 272, # 모델
        'Software': 305, # 프로그램명
        'DateTime': 306, # 날짜
    },
    'ifds' : { #_ifds 안에 있는 정보들
        'GPSInfo': 34853, # 위치정보
        # 밑은 34665('ExifOffset')안에 포함된 정보들
        'ExifVersion': 36864, # Exif 버전 
        'DateTimeOriginal': 36867, # 원본촬영시간
        'DateTimeDigitized': 36868, # 디지털화된시간
        'Flash': 37385, # 플래시  
        'ImageUniqueID':  42016 # 이미지 ID
    }
}

# 기본 EXIF 데이터
DEFUALT_EXIF = (
    b'Exif\x00\x00II*\x00\x08\x00\x00\x00\x06\x00\x1a\x01\x05\x00\x01\x00\x00\x00V\x00\x00\x00\x1b\x01\x05\x00\x01\x00\x00\x00^\x00\x00\x00(\x01\x03\x00\x01\x00\x00\x00\x02\x00\x00\x00\x13\x02\x03\x00\x01\x00\x00\x00\x01\x00\x00\x00i\x87\x04\x00\x01\x00\x00\x00f\x00\x00\x00%\x88\x04\x00\x01\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x00H\x00\x00\x00\x01\x00\x00\x00H\x00\x00\x00\x01\x00\x00\x00\x07\x00\x00\x90\x07\x00\x04\x00\x00\x000221\x01\x91\x01\x00\x04\x00\x00\x00\x01\x02\x03\x00\x00\xa0\x07\x00\x04\x00\x00\x000100\x01\xa0\x03\x00\x01\x00\x00\x00\x01\x00\x00\x00\x02\xa0\x03\x00\x01\x00\x00\x00 \x03\x00\x00\x03\xa0\x03\x00\x01\x00\x00\x00+\x04\x00\x00\x06\xa4\x03\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\x01\x00\x04\x00\x00\x00\x02\x02\x00\x00\x01\x00\x02\x00\x02\x00\x00\x00N\x00\x00\x00\x02\x00\x0c\x00\x03\x00\x00\x00>\x01\x00\x00\x03\x00\x02\x00\x02\x00\x00\x00E\x00\x00\x00\x04\x00\x0c\x00\x03\x00\x00\x00V\x01\x00\x00\x05\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x06\x00\x0c\x00\x01\x00\x00\x00n\x01\x00\x00\x07\x00\x0c\x00\x03\x00\x00\x00v\x01\x00\x00\x1b\x00\x01\x00\x0c\x00\x00\x00\x8e\x01\x00\x00\x1d\x00\x02\x00\x0b\x00\x00\x00\x9a\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00ASCII\x00\x00\x00GPS\x000000:00:00\x00\x00'
)

# 위도, 경도 이용해서 도/분/초 얻기
def get_DegMinSec(lat, lon, tmp) -> Optional[Iterable[int]]:
    try:
        # 위도
        latDeg = int(lat) # 도
        latMin = int((lat-latDeg)*60) # 분
        latSec = round(((lat-latDeg)* 60 - latMin) * 60, 5) # 초
        # 남/북 판별
        latStr = 'N' # 남위
        if lat < 0 : latStr = 'S' # 북위

        # 경도
        lonDeg = int(lon)
        lonMin = int((lon-lonDeg)*60)
        lonSec = round(((lon-lonDeg)* 60 - lonMin) * 60, 5)
        # 동/서 판별
        lonStr = 'E' # 동경
        if lon < 0 : lonStr = 'W' # 서경

        tmp[1] = latStr
        tmp[2] = (float(latDeg), float(latMin), latSec)
        tmp[3] = lonStr
        tmp[4] = (float(lonDeg), float(lonMin), lonSec)

        return tmp
    except Exception as E:
        logging.error(E)
        return None


# EXIF 수정하기
def edit_exif_data(img_path, usr_data_list) -> Optional[BytesIO]:
    try:
        img = Image.open(img_path)
        exif_data = img._exif
        exifs=img._getexif()
    except Exception as E: # 이미지를 불러올 수 없는 경우
        img.close()
        logging.error(E)
        return None
    
    # EXIF 데이터가 없거나 GPS 데이터가 없는 경우
    if (not exif_data) or (not 34853 in exifs):
        exif_data = Image.Exif()
        exif_data.load(DEFUALT_EXIF) # 미리 만들어둔 기본 EXIF 데이터 불러오기
    
    exif_data.tobytes() # _ifds, _data를 생성하기 위해 실행
    
    try:
        for usr_data in usr_data_list: # 사용자가 보낸 수정값
            data = usr_data_list[usr_data] # 수정값 Value
            if usr_data in SELECT_LIST_FOR_EDIT["data"]: # _data 안에 있는 경우
                sel = SELECT_LIST_FOR_EDIT["data"][usr_data] # exif 태그 값으로 변경
                if data is None:
                    exif_data._data.pop(sel, None) # 제거
                else:
                    exif_data._data[sel] = data
            elif usr_data in SELECT_LIST_FOR_EDIT["ifds"]: # _ifds 안에 있는 경우
                sel = SELECT_LIST_FOR_EDIT["ifds"][usr_data] # exif 태그 값으로 변경
                if usr_data == 'GPSInfo': # GPS 정보인경우
                    if data is not None: # GPS 수정값 있으면
                        gps_tmp = get_DegMinSec(data[0], data[1], exif_data._ifds[34853])
                        if gps_tmp: # GPS 정보가 정상적인 경우
                            exif_data._ifds[34853] = gps_tmp
                    else: # GPS 수정값 없으면
                        exif_data._ifds[34853] = {} # 제거
                if data is None:
                    exif_data._ifds[34665].pop(sel, None) # 제거
                else:
                    exif_data._ifds[34665][sel] = data
        # Pillow.image -> ByteIo로 변환
        img_io = BytesIO()
        img.save(img_io, 'JPEG', exif=exif_data, quality=70) # 사진 바이트로 변환후 반환하기
        img.close()
        img_io.seek(0)
        return img_io
    except Exception as E: # 수정 도중 에러 발생시
        img.close()
        logging.error(E)
        return None