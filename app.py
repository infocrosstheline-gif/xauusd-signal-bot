"""
XAU/USD Trading Signal Server
TradingView Webhook → Flask Server → Telegram
"""
from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime
app = Flask(__name__)
# ── Konfiguration ──────────────────────────
TELEGRAM_TOKEN   = "8715502561:AAEk29LfHsm7RPcZlpNw7SxaLhJGV5ZAQV4"
TELEGRAM_CHAT_ID = "823680565"
WEBHOOK_SECRET   = "xauusd_secret_2024"  # Sicherheitsschlüssel
# ── Telegram Nachricht senden ──────────────
def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, data=data, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"Telegram Fehler: {e}")
        return False
# ── Signal Nachricht bauen ─────────────────
def build_message(data: dict) -> str:
    direction  = data.get("direction", "UNKNOWN")
    pattern    = data.get("pattern", "Unbekannt")
    timeframe  = data.get("timeframe", "?")
    probability = data.get("probability", 0)
    price      = data.get("price", 0)
    sl         = data.get("sl", 0)
    tp1        = data.get("tp1", 0)
    tp2        = data.get("tp2", 0)
    h1_bias    = data.get("h1_bias", "NEUTRAL")
    reasons    = data.get("reasons", [])
    bart       = data.get("bart", False)
    emoji = " " if direction == "LONG" else " "
    bias_emoji = {"BULLISH": " ", "BEARISH": " ", "NEUTRAL": " "}.get(h1_bias, " ")
    if probability >= 80:
        prob_emoji = " "
    elif probability >= 70:
        prob_emoji = " "
    elif probability >= 60:
        prob_emoji = " "
    else:
        prob_emoji = " "
    msg = f"""
╔════════════════════════╗
  {emoji} *XAU/USD SIGNAL* {emoji}
╚════════════════════════╝
 Richtung: *{direction}*
{prob_emoji} Wahrscheinlichkeit: *{probability}%*
 Pattern: *{pattern}*
 Timeframe: *{timeframe}*
 Entry:     `{price}`
 Stop Loss: `{sl}`
 TP1:       `{tp1}`
 TP2:       `{tp2}`
{bias_emoji} H1 Trend: *{h1_bias}*
"""
    if bart:
        msg += "\n *BART PATTERN auf H1 erkannt!*\n"
        msg += " Starke Bewegung möglich!\n"
    if reasons:
        msg += "\n *Bestätigungen:*\n"
        for r in reasons:
            msg += f"  {r}\n"
    msg += f"\n `{datetime.utcnow().strftime('%d.%m.%Y %H:%M')} UTC`"
    msg += "\n\n_ Kein Finanzrat. Eigene Analyse!_"
    return msg.strip()
# ── Webhook Endpoint ───────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Sicherheitsprüfung
        secret = request.headers.get("X-Secret", "")
        if secret != WEBHOOK_SECRET:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data"}), 400
        print(f" Signal empfangen: {data}")
        msg = build_message(data)
        success = send_telegram(msg)
        if success:
            print(" Signal an Telegram gesendet!")
            return jsonify({"status": "ok"}), 200
        else:
            return jsonify({"error": "Telegram failed"}), 500
    except Exception as e:
        print(f" Fehler: {e}")
        return jsonify({"error": str(e)}), 500
# ── Health Check ───────────────────────────
@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": " XAU/USD Signal Server läuft!",
        "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    })
# ── Test Endpoint ──────────────────────────
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
        "reasons": [
            " EMA 9/21 Bullish Crossover",
            "
 RSI überverkauft (34.2)",
            "
            "
            "
        ]
    }
 Bullish Engulfing",
 MACD positiv",
 Preis an unterem Bollinger Band"
    msg = build_message(test_data)
    send_telegram(msg)
    return jsonify({"status": "Test Signal gesendet!"}), 200
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
