const translations = {
  ko: {
    title: "대만어 변조 분석기",
    description:
      "한자 문장을 입력하면 공식 로마자 표기, 단어 분절, 변조 결과를 함께 표시합니다.",

    inputLabel: "대만어 한자 문장",
    analyze: "분석",
    sample: "예문",

    officialNotation: "공식 표기",
    segmentation: "단어 분절",
    sandhiResult: "변조 결과",
    tailoTranscription: "Tai-lo 전사",
    pojTranscription: "POJ 전사",
    copy: "복사",

    listenSuisiann: "SuiSiann에서 들어보기 ↗",

    transcriptionBefore: "",
    transcriptionTerm: "Tai-lo / POJ 전사",
    transcriptionNote:
      "는 내부 변조 결과를 읽기 쉽게 Tai-lo와 POJ로 다시 표시한 파생 표기입니다. 실제 음향 결과 자체를 전사한 것은 아닙니다.",

    tone10Before:
      "내부 tone 10은 Tai-lo / POJ 전사에서 checked tone 4 표기형으로 표시하며, 내부 값은 위의 ",
    tone10After: "에 그대로 남깁니다.",

    usage: "[ 사용 안내 ]",
    licenses: "Licenses",
    close: "닫기",

    usageTitle: "사용 안내",
    usage1:
      "이 도구는 대만어 연독변조의 정답을 제공하기 위한 것이 아니라, 변조 규칙을 학습하고 결과를 확인하기 위한 보조 도구입니다.",
    usage2:
      "관련 변조 알고리즘 연구에서는 테스트 데이터 기준 88.90%의 정확도가 보고되었습니다. 이는 현재 웹앱 자체의 정확도를 의미하지 않으며, 프로그램의 결과가 실제 발화와 다를 수 있습니다.",
    usage3:
      "학습할 때는 원래 성조 표기를 보고 먼저 직접 변조를 추측한 뒤, 프로그램의 결과를 확인하고, 마지막으로 실제 화자의 발화와 비교하는 방식으로 사용하는 것을 권장합니다.",
    usage4:
      "프로그램의 출력은 항상 정답으로 간주하기보다, 변조의 방향을 확인하기 위한 참고 자료로 활용해 주세요.",

    emptyInput: "문장을 입력하세요.",
    analyzing: "분석 중…",
    analysisFailed: "분석에 실패했습니다.",
    copied: "완료",
  },

  "zh-TW": {
    title: "台語變調分析器",
    description: "輸入台語漢字句子，即可查看羅馬字、分詞與連讀變調結果。",

    inputLabel: "台語漢字句子",
    analyze: "分析",
    sample: "例句",

    officialNotation: "原始標記",
    segmentation: "單詞分節",
    sandhiResult: "變調結果",
    tailoTranscription: "台羅轉寫",
    pojTranscription: "白話字轉寫",
    copy: "複製",

    listenSuisiann: "在 SuiSiann 聽看看 ↗",

    transcriptionBefore: "",
    transcriptionTerm: "台羅／白話字轉寫",
    transcriptionNote:
      "是將內部變調結果重新以較易閱讀的台羅與白話字表示的衍生標記，並不是對實際語音結果的直接轉寫。",

    tone10Before:
      "內部 tone 10 在台羅／白話字轉寫中以 checked tone 4 的形式顯示；內部數值則保留於上方的",
    tone10After: "中。",

    usage: "[ 使用說明 ]",
    licenses: "Licenses",
    close: "關閉",

    usageTitle: "使用說明",
    usage1:
      "這個工具並不是用來提供台語連讀變調的標準答案，而是協助學習變調規則與確認結果的輔助工具。",
    usage2:
      "相關的變調演算法研究在測試資料中報告了 88.90% 的正確率。這並不代表目前這個網站本身的正確率，程式輸出的結果仍可能與實際發音不同。",
    usage3:
      "學習時，建議先根據原本的聲調標記自行推測變調，再確認程式計算出的結果，最後與真人實際說話的錄音進行比較。",
    usage4:
      "請不要將程式輸出一律視為正確答案，而是把它當作確認變調方向並與實際發音比較的參考資料。",

    emptyInput: "請輸入句子。",
    analyzing: "分析中…",
    analysisFailed: "分析失敗。",
    copied: "完成",
  },

  en: {
    title: "Taiwanese Tone Sandhi Analyzer",
    description:
      "Enter a Taiwanese Hokkien sentence in Han characters to view romanization, word segmentation, and tone sandhi results.",

    inputLabel: "Taiwanese Hokkien sentence in Han characters",
    analyze: "Analyze",
    sample: "Example",

    officialNotation: "Original notation",
    segmentation: "Word segmentation",
    sandhiResult: "Tone sandhi result",
    tailoTranscription: "Tai-lo transcription",
    pojTranscription: "POJ transcription",
    copy: "Copy",

    listenSuisiann: "Listen on SuiSiann ↗",

    transcriptionBefore: "The ",
    transcriptionTerm: "Tai-lo / POJ transcriptions",
    transcriptionNote:
      " are derived representations of the internal tone-sandhi result in a more readable form. They are not transcriptions of actual acoustic output.",

    tone10Before:
      "Internal tone 10 is rendered as checked tone 4 in the Tai-lo / POJ transcriptions, while the internal value is preserved in the ",
    tone10After: " above.",

    usage: "[ Usage ]",
    licenses: "Licenses",
    close: "Close",

    usageTitle: "Usage",
    usage1:
      "This tool is intended as an aid for learning and checking Taiwanese Hokkien tone sandhi, not as a source of definitive answers.",
    usage2:
      "Related research on a tone-sandhi algorithm reported an accuracy of 88.90% on test data. This figure does not represent the accuracy of this web app itself, and its output may differ from actual speech.",
    usage3:
      "For learning, we recommend first predicting the sandhi from the original tone notation, then checking the program's result, and finally comparing the sentence with recordings of actual speakers.",
    usage4:
      "The output should be used as a reference for checking the direction of tone sandhi and comparing it with actual speech, rather than being treated as invariably correct.",

    emptyInput: "Enter a sentence.",
    analyzing: "Analyzing…",
    analysisFailed: "Analysis failed.",
    copied: "Copied",
  },
};
