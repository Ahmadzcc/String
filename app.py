import os
import asyncio
from flask import Flask, request, jsonify, render_template
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import pytz
from datetime import datetime

app = Flask(__name__)
hash_store = {}

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
        sent = await client.send_code_request(phone)
        hash_store[phone] = {
            "hash": sent.phone_code_hash,
            "session": session.save(),
            "api_id": api_id,
            "api_hash": api_hash,
        }
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
    code = data.get("code")
    password = data.get("password", "").strip()

    if phone not in hash_store:
        return jsonify({"error": "لم يتم إرسال كود مسبقًا لهذا الرقم"})

    phone_hash_data = hash_store[phone]
    phone_code_hash = phone_hash_data["hash"]
    api_id = phone_hash_data["api_id"]
    api_hash = phone_hash_data["api_hash"]
    session_str = phone_hash_data["session"]

    async def run():
        session = StringSession(session_str)
        client = TelegramClient(session, api_id, api_hash)
        await client.connect()
        try:
            await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        except SessionPasswordNeededError:
            if not password:
                return {"error": "تم تفعيل التحقق بخطوتين. يرجى إدخال كلمة المرور."}
            try:
                await client.sign_in(password=password)
            except Exception as pw_error:
                return {"error": f"كلمة المرور غير صحيحة: {str(pw_error)}"}
        except Exception as e:
            return {"error": str(e)}

        string_session = session.save()
        msg = f"تم استخراج الجلسة بواسطة @Tepthon\n\nالكود: `{code}`\n**ملاحظة: لا تشارك الكود مع أحد**"
        await client.send_message("me", msg, parse_mode="markdown")
        await client.send_message("me", f"`{string_session}`")
        await client.disconnect()
        return {"session": string_session}

    try:
        result = asyncio.run(run())
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
