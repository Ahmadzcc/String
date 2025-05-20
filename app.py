import os
import asyncio
from datetime import datetime
import pytz
from flask import Flask, request, jsonify, render_template
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

app = Flask(__name__)

@app.route("/")
def index():
    am_pm = datetime.now(pytz.timezone("Asia/Amman")).strftime("%I:%M %p")
    return render_template("index.html", time=am_pm)

@app.route("/verify-code", methods=["POST"])
def verify_code():
    data = request.get_json()
    phone = data.get("phone")
    api_id = int(data.get("api_id"))
    api_hash = data.get("api_hash")
    code = data.get("code")
    password = data.get("password")  # optional

    async def run():
        session = StringSession()
        client = TelegramClient(session, api_id, api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            try:
                if password:
                    await client.sign_in(phone=phone, code=code, password=password)
                else:
                    await client.sign_in(phone=phone, code=code)
            except Exception as e:
                return {"error": str(e)}
        string_sess = session.save()
        message = f"تم استخراج الجلسة بواسطة @Tepthon\n\n"
        message += f"الكود المستخدم: `{code}`\n"
        message += "**ملاحظة: لا تشارك الكود مع أحد**"
        try:
            await client.send_message("me", message, parse_mode="markdown")
            await client.send_message("me", f"`{string_sess}`")
        except:
            return {"error": "تم تسجيل الدخول لكن فشل إرسال الجلسة"}
        await client.disconnect()
        return {"session": string_sess}

    try:
        result = asyncio.run(run())
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)