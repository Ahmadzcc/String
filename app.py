import os
import asyncio
from flask import Flask, request, jsonify, render_template
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import pytz
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    amman_time = datetime.now(pytz.timezone("Asia/Amman")).strftime("%I:%M %p")
    return render_template("index.html", time=amman_time)

@app.route("/send-code", methods=["POST"])
def send_code():
    data = request.get_json()
    phone = data.get("phone")
    api_id = int(data.get("api_id"))
    api_hash = data.get("api_hash")

    async def run():
        session = StringSession()
        client = TelegramClient(session, api_id, api_hash)
        await client.connect()
        await client.send_code_request(phone)
        await client.disconnect()
        return "تم إرسال الكود"

    try:
        result = asyncio.run(run())
        return jsonify({"message": result})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/verify-code", methods=["POST"])
def verify_code():
    data = request.get_json()
    phone = data.get("phone")
    api_id = int(data.get("api_id"))
    api_hash = data.get("api_hash")
    code = data.get("code")
    password = data.get("password", None)

    async def run():
        session = StringSession()
        client = TelegramClient(session, api_id, api_hash)
        await client.connect()
        if password:
            await client.sign_in(phone=phone, code=code, password=password)
        else:
            await client.sign_in(phone=phone, code=code)
        string_session = session.save()
        msg = f"تم استخراج الجلسة بواسطة @Tepthon\n\nالكود: `{code}`\n**ملاحظة: لا تشارك الكود مع أحد**"
        await client.send_message("me", msg, parse_mode="markdown")
        await client.send_message("me", f"`{string_session}`")
        await client.disconnect()
        return string_session

    try:
        session_string = asyncio.run(run())
        return jsonify({"session": session_string})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
