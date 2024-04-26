from datetime import datetime
from eudplib import *

settings: dict[str]
# [출처] 맵 제목, 설명, 포스 이름 자동 생성하기 ([스에아]스타 에디터 아카데미-스타크래프트 리마스터 대표 카페) | 작성자 Artanis

now = datetime.now().date().isoformat()

def convert2b2(original):
	return i2b2(GetStringIndex(original.replace('(날짜)', now)))

def set_text():
	chkt = GetChkTokenized()	
	SPRP = bytearray(chkt.getsection("SPRP"))
	FORC = bytearray(chkt.getsection("FORC"))

	for key in 'map_name', 'map_desc', 'force1_name', 'force2_name':
		assert key in settings, key + "이 설정되지 않았습니다."

	SPRP[0:2] = convert2b2(settings['map_name'])
	SPRP[2:4] = convert2b2(settings['map_desc'])
	FORC[8:10] = convert2b2(settings['force1_name'])
	FORC[10:12] = convert2b2(settings['force2_name'])

	chkt.setsection("SPRP", SPRP)
	chkt.setsection("FORC", FORC)

set_text()

import pathlib
print(pathlib.Path().resolve())
