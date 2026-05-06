from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime
app = Flask(__name__)
TELEGRAM_TOKEN   = "8715502561:AAEk29LfHsm7RPcZlpNw7SxaLhJGV5ZAQV4"
TELEGRAM_CHAT_ID = "823680565"
WEBHOOK_SECRET   = "xauusd_secret_2024"
def send_telegram(message):
    url  = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, data=data, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False
def build_message(data):
    direction   = data.get("direction", "UNKNOWN")
    pattern     = data.get("pattern", "Unknown")
    timeframe   = data.get("timeframe", "?")
    probability = data.get("probability", 0)
    price       = data.get("price", 0)
    sl          = data.get("sl", 0)
    tp1         = data.get("tp1", 0)
    tp2         = data.get("tp2", 0)
    h1_bias     = data.get("h1_bias", "NEUTRAL")
    reasons     = data.get("reasons", [])
    bart        = data.get("bart", False)
    arrow     = "LONG >>" if direction == "LONG" else "SHORT <<"
    bias_icon = "[BULLISH]" if h1_bias == "BULLISH" else "[BEARISH]" if h1_bias == "BEARISH" else "[NEUTRAL]"
    prob_icon = "STARK" if probability >= 80 else "GUT" if probability >= 70 else "OK"
    msg = (
        "========================\n"
        f"XAU/USD SIGNAL - {arrow}\n"
        "========================\n\n"
        f"Richtung: *{direction}*\n"
        f"Wahrscheinlichkeit: *{probability}%* ({prob_icon})\n"
        f"Pattern: *{pattern}*\n"
        f"Timeframe: *{timeframe}*\n\n"
        f"Entry:     `{price}`\n"
        f"Stop Loss: `{sl}`\n"
        f"TP1:       `{tp1}`\n"
        f"TP2:       `{tp2}`\n\n"
        f"H1 Trend: *{h1_bias}* {bias_icon}\n"
    )
    if bart:
        msg += "\nACHTUNG: BART PATTERN auf H1!\n"
    if reasons:
        msg += "\nBestaetigungen:\n"
        for r in reasons:
            msg += f"  - {r}\n"
    msg += f"\nZeit: `{datetime.utcnow().strftime('%d.%m.%Y %H:%M')} UTC`"
    msg += "\n\n_Kein Finanzrat. Eigene Analyse!_"
    return msg
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        secret = request.headers.get("X-Secret", "")
        if secret != WEBHOOK_SECRET:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data"}), 400
        msg     = build_message(data)
        success = send_telegram(msg)
        if success:
            return jsonify({"status": "ok"}), 200
        else:
            return jsonify({"error": "Telegram failed"}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "XAU/USD Signal Server running!",
        "time":   datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    })
@app.route("/test", methods=["GET"])
def test():
    test_data = {
        "direction":   "LONG",
        "pattern":     "Bullish Engulfing + EMA Crossover",
        "timeframe":   "M15",
        "probability": 78,
        "price":       "2345.20",
        "sl":          "2341.80",
        "tp1":         "2348.60",
        "tp2":         "2352.00",
        "h1_bias":     "BULLISH",
        "bart":        False,
        "reasons":     ["EMA Crossover", "RSI ueberverkauft", "Bullish Engulfing"]
    }
    msg = build_message(test_data)
    send_telegram(msg)
    return jsonify({"status": "Test Signal sent!"}), 200
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
