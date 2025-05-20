import os
from flask import Flask, request, jsonify, render_template
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send-code", methods=["POST"])
def send_code():
    data = request.get_json()
    phone = data.get("phone")
    api_id = data.get("api_id")
    api_hash = data.get("api_hash")

    if not all([phone, api_id, api_hash]):
        return jsonify({"error": "Missing data"}), 400

    try:
        session = StringSession()
        client = TelegramClient(session, int(api_id), api_hash)
        client.connect()
        if not client.is_user_authorized():
            client.send_code_request(phone)
        client.disconnect()
        return jsonify({"message": "Code sent successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/verify-code", methods=["POST"])
def verify_code():
    data = request.get_json()
    phone = data.get("phone")
    api_id = data.get("api_id")
    api_hash = data.get("api_hash")
    code = data.get("code")

    if not all([phone, api_id, api_hash, code]):
        return jsonify({"error": "Missing data"}), 400

    try:
        session = StringSession()
        client = TelegramClient(session, int(api_id), api_hash)
        client.connect()
        if not client.is_user_authorized():
            client.sign_in(phone, code)
        client.disconnect()
        return jsonify({"session": session.save()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)