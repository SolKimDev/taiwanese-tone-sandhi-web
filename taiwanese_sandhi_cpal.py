# -*- coding: utf-8 -*-

"""
This file contains code adapted from 臺灣言語工具.

Original project:
https://github.com/i3thuan5/tai5-uan5_gian5-gi2_kang1-ku7

License: Common Public Attribution License 1.0 (CPAL-1.0)

This modification extracts/adapts the Taiwanese tone-sandhi application
logic for use in this web application.

Modification date: 2026-08-28
"""

from 臺灣言語工具.語音合成.閩南語音韻.變調判斷 import 變調判斷
from 臺灣言語工具.音標系統.閩南語.臺灣閩南語羅馬字拼音 import (
    臺灣閩南語羅馬字拼音,
)


def apply_taiwanese_sandhi(sentence):
    result = sentence.轉音(
        臺灣閩南語羅馬字拼音,
        函式="音值",
    )

    decisions = 變調判斷.判斷(result)
    index = 0

    for word, original_word in zip(
        result.網出詞物件(),
        sentence.網出詞物件(),
    ):
        new_chars = []

        for char, original_char in zip(
            word.內底字,
            original_word.內底字,
        ):
            rule = decisions[index]

            if rule == 變調判斷.愛提掉的:
                pass
            else:
                if char.音 == (None,):
                    new_chars.append(original_char.khóopih字())
                else:
                    char.音 = "".join(rule.變調(char.音))
                    new_chars.append(char)

            index += 1

        word.內底字 = new_chars

    return result.看音()
