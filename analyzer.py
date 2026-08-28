# -*- coding: utf-8 -*-
"""
臺灣言語工具 변조 STR 실행기 v4

출력
----
Tai-lo原>  변조 전 기본 臺羅(KIP)
POJ原>      변조 전 기본 POJ(白話字)
통사구조>   Tau-Phah-Ji의 分詞 결과
變調>       臺灣言語工具의 내부 변조/음가 STR
POJ變調>    변조된 성조를 '본성조식 POJ 성조부호'로 다시 표기한 가독용 문자열

중요
----
- POJ變調는 臺灣言語工具의 내부 변조 결과를 사람이 읽기 편하게
  POJ 표기로 되돌린 "표시용" 결과다.
- 내부 tone 10은 일반 POJ에 독립적인 diacritic이 없으므로,
  사용자가 읽는 전통적 변조 결과에 맞춰 checked tone 4 표기형으로 렌더링한다.
  예: ta̍k8 -> 내부 tak10 -> POJ變調 tak
- 실제 내부 값 자체는 變調> 줄에서 그대로 보존한다.
"""

import re

from tauphahji_cmd import tàuphahjī
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.語音合成 import 台灣話口語講法
from 臺灣言語工具.音標系統.閩南語.臺灣閩南語羅馬字拼音 import (
    臺灣閩南語羅馬字拼音
)

EXIT_WORDS = {":q", ":quit", "q", "quit", "exit"}

# 내부 음가 문자열에서 각 음절 끝의 tone label을 뽑기 위한 패턴
TONE_RE = re.compile(r"(\d+)$")


def tailo_to_poj_syllable(syllable: str) -> str:
    """臺羅 한 음절을 POJ 성조부호 표기로 변환한다."""
    obj = 臺灣閩南語羅馬字拼音(syllable)
    result = obj.轉白話字()
    if result is None:
        return syllable
    return result


def tailo_text_to_poj(text: str) -> str:
    """
    臺羅 문장을 POJ로 변환.
    공백/하이픈/문장부호를 최대한 보존한다.
    """
    # 음절 후보와 비음절 구분기호를 분리
    parts = re.split(r"([ \t\-]+|[，。！？!?、；;：:（）()\[\]「」『』…])", text)
    out = []

    for part in parts:
        if not part:
            continue
        if re.fullmatch(r"[ \t\-]+|[，。！？!?、；;：:（）()\[\]「」『』…]", part):
            out.append(part)
            continue

        # 기타 punctuation이 음절 뒤에 붙어 있을 수 있음
        m = re.match(r"^(.*?)([^\w\u00C0-\u02FF\u0300-\u036Fⁿ͘]*)$", part, re.UNICODE)
        core = m.group(1) if m else part
        tail = m.group(2) if m else ""

        if core:
            out.append(tailo_to_poj_syllable(core))
        out.append(tail)

    return "".join(out)


def extract_sandhi_tones(sandhi_str: str):
    """
    台灣話口語講法()의 내부 STR에서 음절 순서대로 tone label 추출.
    punctuation token은 제외.
    """
    tones = []

    # 하이픈과 공백 모두 음절 경계로 취급
    tokens = re.split(r"[\s\-]+", sandhi_str.strip())
    for tok in tokens:
        tok = tok.strip()
        if not tok:
            continue
        m = TONE_RE.search(tok)
        if m:
            tones.append(m.group(1))

    return tones


def split_tailo_syllables(text: str):
    """
    臺羅 문자열에서 실제 음절만 순서대로 추출.
    반환: [(syllable, separator_after), ...] 대신,
    재조립이 쉽도록 token stream 생성.
    """
    # 하이픈/공백/문장부호를 별도 token으로 보존
    tokens = re.split(r"([ \t\-]+|[，。！？!?、；;：:（）()\[\]「」『』…])", text)
    return [t for t in tokens if t != ""]


def change_tone_numeric_tailo(syllable: str, new_tone: str) -> str:
    """
    원래 臺羅 음절의 성·운을 유지하면서 새 tone number를 적용한 숫자조 臺羅를 만든다.
    그 뒤 POJ 변환용으로 사용한다.

    tone 10은 사용자 표시 목적상 tone 4로 렌더링한다.
    """
    obj = 臺灣閩南語羅馬字拼音(syllable)
    if obj.音標 is None:
        return syllable

    # tone 10은 일반 POJ '본성조식' 표시에 독립 부호가 없으므로 4로 표시.
    display_tone = "4" if new_tone == "10" else new_tone

    # 경성 등은 일단 기존 라이브러리의 numeric parser에 맡김
    prefix = ""
    if getattr(obj, "輕", "") in ("0", "--"):
        prefix = obj.輕

    # 성 + 운 + 새 숫자조
    return f"{prefix}{obj.聲}{obj.韻}{display_tone}"


def sandhi_poj_from_tailo_and_internal(tailo: str, sandhi_str: str) -> str:
    """
    원래 臺羅 음절열 + 내부 변조 tone label을 합쳐
    '변조된 성조를 POJ 본성조 표기법으로 표시'한 문자열 생성.
    """
    tones = extract_sandhi_tones(sandhi_str)
    tokens = split_tailo_syllables(tailo)

    out = []
    tone_idx = 0

    for tok in tokens:
        # 구분기호/문장부호
        if re.fullmatch(r"[ \t\-]+|[，。！？!?、；;：:（）()\[\]「」『』…]", tok):
            out.append(tok)
            continue

        # punctuation이 뒤에 붙은 경우 분리
        m = re.match(r"^(.*?)([^\w\u00C0-\u02FF\u0300-\u036Fⁿ͘]*)$", tok, re.UNICODE)
        core = m.group(1) if m else tok
        tail = m.group(2) if m else ""

        if not core:
            out.append(tok)
            continue

        if tone_idx >= len(tones):
            # 혹시 내부 STR과 음절 수가 다르면 원형 POJ로 안전하게 표시
            out.append(tailo_to_poj_syllable(core) + tail)
            continue

        numeric_tailo = change_tone_numeric_tailo(core, tones[tone_idx])
        poj_obj = 臺灣閩南語羅馬字拼音(numeric_tailo)
        poj = poj_obj.轉白話字()

        if poj is None:
            poj = numeric_tailo

        out.append(poj + tail)
        tone_idx += 1

    return "".join(out)


def analyze(text: str):
    tau = tàuphahjī(text)

    hanji = tau["漢字"]
    tailo = tau["KIP"]
    segmentation = tau["分詞"]

    sentence = 拆文分析器.建立句物件(hanji, tailo)
    sandhi = 台灣話口語講法(sentence)

    poj_original = tailo_text_to_poj(tailo)
    poj_sandhi = sandhi_poj_from_tailo_and_internal(tailo, sandhi)

    return {
        "漢字": hanji,
        "Tai-lo原": tailo,
        "POJ原": poj_original,
        "通사구조": segmentation,
        "變調": sandhi,
        "POJ變調": poj_sandhi,
    }


