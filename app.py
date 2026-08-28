# -*- coding: utf-8 -*-
from flask import Flask, jsonify, render_template, request

from analyzer import analyze

app = Flask(__name__)
app.json.ensure_ascii = False


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.post("/api/analyze")
def api_analyze():
    payload = request.get_json(silent=True) or {}
    text = str(payload.get("text", "")).strip()

    if not text:
        return jsonify({"ok": False, "error": "분석할 대만어 한자 문장을 입력하세요."}), 400

    if len(text) > 1000:
        return jsonify({"ok": False, "error": "입력은 1000자 이하로 제한됩니다."}), 400

    try:
        result = analyze(text)
    except Exception:
        app.logger.exception("Analysis failed")
        return jsonify({
            "ok": False,
            "error": "분석 중 오류가 발생했습니다."
        }), 500

    return jsonify({"ok": True, "result": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
