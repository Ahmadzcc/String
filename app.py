
from flask import Flask, request, jsonify, render_template
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send-code", methods=["POST"])
def send_code():
    data = request.json
    phone = data.get("phone")
    api_id = int(data.get("api_id"))
    api_hash = data.get("api_hash")

    print("=== RECEIVED /send-code ===")
    print("Phone:", phone)
    print("API ID:", api_id)
    print("API HASH:", api_hash)

    async def run():
        async with TelegramClient(StringSession(), api_id, api_hash) as client:
            return await client.send_code_request(phone)

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run())
        print(">>> CODE HASH:", result.phone_code_hash)
        return jsonify({"phone_code_hash": result.phone_code_hash})
    except Exception as e:
        print(">>> ERROR from Telegram:", str(e))
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)"
