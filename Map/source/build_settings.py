from typing import Dict
from eudplib import *
import json
import pathlib
import re
import codecs
import inspect

from main import settings

settings: Dict[str, str]

choseongs = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ',
             'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
SEGMENT_LENGTH = 2.28
ESCAPE_SEQUENCE_RE = re.compile(r"(\\x..)|(\\n)")


def decode_match(match):
    return codecs.decode(match.group(0), 'unicode-escape')


def escape_hex_newline(s):
    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)


def extract_choseong(s):
    return "".join(choseongs[choseong_index] if 0 <= (choseong_index := (ord(c) - ord('가')) // 588) < len(choseongs)
                   else c for c in s)


def init():
    # 흑마법구간 시작
    for frame_info in inspect.stack():
        if frame_info.function != 'loadPluginsFromConfig':
            continue
        chatEvent_settings: Dict[str, str] = frame_info.frame.f_locals['config']['chatEvent']
        break
    else:
        assert False, "정상적으로 EUDDraft를 통해 실행되지 않은 것 같습니다. 확인해 주세요."
    # 흑마법구간 끝

    crawled = pathlib.Path() / "../Crawled/"
    with (crawled / 'cache.json').open(mode='r', encoding='utf-8') as f:
        data = json.load(f)

    music_answer = []
    answer_key = []
    music_hint_1 = []
    music_hint_2 = []
    music_length = []
    segment_count = [0]
    answers = {}
    answer_index = 2
    music_index = 1
    ending_music_hashstring = None
    ending_music_segment_count = None
    categories = {category_value.strip(): []
                  for category_value in settings['categories_in_sheet'].split(',')}
    hint2_is_chosung_hint = settings.get(
        'hint2_is_choseong_hint', '').strip() == 'True'

    for entry in data:
        ogg_file = crawled / f"trimmed/{entry['HashString']}-0.ogg"
        if not ogg_file.is_file():  # 파일을 찾지 못한 경우입니다. 크롤러(다운로더)를 돌렸는지 한 번 확인해 보세요.
            print(f"ogg file not found: {entry['OriginalAnswer']}")
            continue

        if entry['OpeningOrEnding'] == '오프닝':
            segment_count[0] = int(entry['SegmentCount'])
            for i in range(segment_count[0]):
                MPQAddFile(f'0-{i}.ogg',
                           (crawled / f"trimmed/{entry['HashString']}-{i}.ogg").open('rb').read())
            continue
        elif entry['OpeningOrEnding'] == '엔딩':
            ending_music_hashstring = entry['HashString']
            ending_music_segment_count = int(entry['SegmentCount'])
            continue

        # 정답 내 알파벳을 전부 소문자로 바꾸는 경우입니다. 대문자도 정답에 인정하려면, .lower()을 제거하세요.
        current_answers = [*{s.replace(" ", "").lower() for s in
                             (entry['AnswerList'] + [entry['OriginalAnswer']] +
                             ([entry['ChoseongHint']] if entry.get('ChoseongHint', None) and hint2_is_chosung_hint else []))}]
        # entry.get을 ~~ in ~~로 대체 못 하는 이유: get 결과물이 None인 경우가 있어서

        current_answer_indices = []

        for answer in current_answers:
            if answer not in answers:
                answers[answer] = answer_index
                answer_index += 1
            current_answer_indices.append(answers[answer])

        current_answer_indices.append(0)
        answer_key.append(current_answer_indices)

        music_answer.append(escape_hex_newline(settings['answer_text_pattern']
                            .replace("(콜론)", ":")
                            .replace("(곡명)", entry['SongTitle'])
                            .replace("(작품명)", entry['OriginalAnswer'])
                            .replace("(범주)", settings[f"category_name_{entry['Category']}"])
                            .replace("(힌트1)", entry['Hint'])
                            .replace("(힌트2)", entry['Hint2'])))

        music_hint_1.append(escape_hex_newline(entry['Hint']))

        longest_hangul_answer = max((s for s in current_answers if
                                     all("가" <= c <= "힣" or c == " " or c in choseongs for c in s)), key=len, default="")

        music_hint_2.append(extract_choseong(
            entry.get('ChoseongHint', "") or longest_hangul_answer) or "초성 힌트 없음" if hint2_is_chosung_hint
            else entry['Hint2'])
        segment_count.append(int(entry['SegmentCount']))
        music_length.append(int(entry['SegmentCount'] * SEGMENT_LENGTH))

        for i in range(segment_count[-1]):
            MPQAddFile(f'{music_index}-{i}.ogg',
                       (crawled / f"trimmed/{entry['HashString']}-{i}.ogg").open('rb').read())

        assert entry['Category'] in categories, f"예상하지 못한 범주 {entry['Category']}가 확인되었습니다. 곡명: {entry['SongTitle']}"
        categories.setdefault(entry['Category'], []).append(music_index)
        music_index += 1

    global \
        AnswerKey, MusicHint1, MusicHint2, CategoryCount, CategoryNames, CategoryDescriptions, CategoryMusics, \
        MusicLength, MusicNumber, MusicAnswer, MinQuestionLength, MusicStart, MusicEnd, \
        VoteNum, EndingMusic, settingName3, settingName4, SegmentCount, leaderboard_text

    AnswerKey = EUDArray([*map(EUDArray, answer_key)])
    MusicHint1 = EUDArray([*map(Db, music_hint_1)])
    MusicHint2 = EUDArray([*map(Db, music_hint_2)])

    assert len(
        categories) <= 7, "종류가 7종류 이하여야 합니다. 7종류 이상을 지원하고 싶다면 build_settings.py, opening.eps를 수정해 주세요."

    CategoryCount = len(categories)
    CategoryNames = EUDArray(
        [*map(Db, (escape_hex_newline(settings[f"category_name_{category}"]) for category in categories))])
    CategoryDescriptions = EUDArray(
        [*map(Db, (escape_hex_newline(settings[f"category_description_{category}"].replace("(곡수)", str(len(musics)))) for category, musics in categories.items()))])
    CategoryMusics = EUDArray(
        [EUDArray(musics + [0]) for musics in categories.values()])

    MusicLength = EUDArray([*music_length])
    MusicNumber = len(music_answer)
    MusicAnswer = EUDArray([*map(Db, music_answer)])
    MinQuestionLength = int(settings['min_question_length'])

    MusicStart = int(settings['hint1_timing'])
    MusicEnd = int(settings['hint2_timing'])
    VoteNum = EUDArray(eval(settings['vote_num']))

    EndingMusic = music_index
    segment_count.append(ending_music_segment_count or 0)
    if ending_music_hashstring is not None:
        for i in range(segment_count[-1]):
            MPQAddFile(f'{EndingMusic}-{i}.ogg',
                       (crawled / f"trimmed/{ending_music_hashstring}-{i}.ogg").open('rb').read())

    SegmentCount = EUDArray(segment_count)

    leaderboard_text = escape_hex_newline(settings['leaderboard_text'])

    settingName3, settingName4 = Db(settings['hint1_name']), Db(settings['hint2_name'])

    for effect_file_name in ['opening_sound_1', 'opening_sound_2', 'click_sound', 'skip_sound', 'correct_sound']:
        if effect_file_name not in settings:
            continue
        MPQAddFile(effect_file_name, (pathlib.Path() /
                   f"effect/{settings[effect_file_name]}").open('rb').read())

    chatEvent_settings.update((k, str(v)) for k, v in answers.items())


init()
