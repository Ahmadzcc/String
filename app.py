import os
import asyncio
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

        async def process():
            await client.connect()
            if not await client.is_user_authorized():
                await client.send_code_request(phone)
            await client.disconnect()

        asyncio.run(process())
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

        async def login():
            await client.connect()
            if not await client.is_user_authorized():
                await client.sign_in(phone, code)
            await client.disconnect()
            return session.save()

        string_session = asyncio.run(login())
        return jsonify({"session": string_session})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
