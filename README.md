# 대만어 변조 분석기 — Web Edition

기존 `taiwanese_tone_sandhi_runner_v4.py`의 분석 로직을 웹에서 사용할 수 있도록 감싼 Flask 배포판입니다.

## 기능

- 한자 입력 → Tau-Phah-Ji의 KIP(Tai-lo) 및 分詞
- `臺灣言語工具`의 `台灣話口語講法()` 변조 결과
- Tai-lo 원형 → POJ 원형
- 내부 변조 tone label → 학습용 `POJ變調`
- JSON API: `POST /api/analyze`

`POJ變調`는 실제 음향 분석값이 아니라, 내부 변조 결과를 읽기 쉬운 POJ 표기로 재구성한 표시용 레이어입니다. 내부 tone 10은 POJ 표시에서 checked tone 4 형태로 렌더링하고, 내부 원값은 `變調` 항목에 보존합니다.

## 로컬 실행

Python 3.9 권장.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

브라우저에서 `http://localhost:8000`을 엽니다.

## Docker 실행

```bash
docker build -t taiwanese-tone-sandhi .
docker run --rm -p 8000:8000 taiwanese-tone-sandhi
```

그 뒤 `http://localhost:8000`을 엽니다.

## Render 배포

1. 이 폴더를 GitHub 저장소에 push합니다.
2. Render에서 **New → Blueprint** 또는 **Web Service**를 선택합니다.
3. 저장소를 연결합니다.
4. `render.yaml`을 사용하면 Docker 배포 설정을 자동으로 읽습니다.
5. 배포가 끝나면 생성된 `*.onrender.com` 주소에서 바로 사용할 수 있습니다.

## API 예시

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"人生的無奈,咱嘛是愛忍耐"}'
```

응답의 핵심 필드:

- `Tai-lo原`
- `POJ原`
- `分詞`
- `變調`
- `POJ變調`

## 라이선스 / 출처

이 프로젝트 자체의 소스 코드는 **MIT License**로 배포합니다. 자세한 내용은 `LICENSE`를 참조하세요.

런타임에서 다음 오픈소스 프로젝트를 사용합니다.

- Tau-Phah-Ji-Command — MIT License
- 臺灣言語工具 — CPAL-1.0

각 의존성의 저작권 고지와 라이선스 정보는 `NOTICE.md`를 참조하세요. 제3자 구성요소에는 각각의 원 라이선스가 계속 적용됩니다.

현재 웹앱은 臺灣言語工具를 수정하지 않고 Python 라이브러리로 사용합니다.
SuiSiann은 이 프로젝트에 포함하거나 백엔드 API로 호출하지 않으며, 사용자가 입력한 문장을 SuiSiann 웹사이트에서 확인할 수 있는 외부 링크만 제공합니다.
