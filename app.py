
import asyncio
from flask import Flask, request, jsonify, render_template
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send_code", methods=["POST"])
def send_code():
    data = request.get_json()
    phone = data.get("phone")
    api_id = int(data.get("api_id"))
    api_hash = data.get("api_hash")

    async def run():
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
        await client.send_code_request(phone)
        await client.disconnect()
        return "تم إرسال الكود"

    try:
        result = asyncio.run(run())
        return jsonify({"status": "ok", "message": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
