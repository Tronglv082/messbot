import os
import sys
import json
import random
import datetime
import pytz
import requests
import wikipedia
from flask import Flask, request
from googlesearch import search

# ================= CẤU HÌNH BOT =================
app = Flask(__name__)

# ĐÃ CẬP NHẬT TOKEN MỚI CỦA BẠN TẠI ĐÂY
ACCESS_TOKEN = "EAAJpiB62hRwBQQjVYulX1G6CRANSKLCZBPxF4UhFSZCCebg7uSGCcZAPOti7jjXgUNZCOOfe624MIZBfuCAZCNfaZANLCcKxO3QSomx8mW4xhbOlGzsXwrKDiuO5avRfDnP4DNQdrZB26ni8IZCfqdzjczrbITe2snoFBZBJDUNxxUZC922FvjuIZArIwLN6nqjvwb7HxWNGxIkWawZDZD"
VERIFY_TOKEN = "bot 123"

# Cấu hình ngôn ngữ cho Wikipedia
try:
    wikipedia.set_lang("vi")
except:
    pass

# Biến lưu trạng thái game
kbb_state = {} 

# Data giả lập
GAME_CODES = {
    "genshin": ["GENSHINGIFT", "CA3BLTURGH9D", "RTJUNRSHTREW"],
    "hsr": ["STARRAILGIFT", "HSRVER10JRL", "MB6N2TVCSQ9F"],
    "wuwa": ["WUWA2024", "WUTHERINGGIFT"],
    "wwm": ["WWMVIETNAM", "KIEMHIEP2025"]
}

TAROT_CARDS = [
    {"name": "The Fool", "meaning": "Khởi đầu mới, tự do, ngây thơ."},
    {"name": "The Magician", "meaning": "Sức mạnh ý chí, kỹ năng, sự tập trung."},
    {"name": "The Lovers", "meaning": "Tình yêu, sự hòa hợp, sự lựa chọn."},
    {"name": "Death", "meaning": "Kết thúc để bắt đầu, sự thay đổi lớn."},
    {"name": "The Sun", "meaning": "Thành công, niềm vui, năng lượng tích cực."},
]

# ================= HÀM GỬI TIN =================

def send_message(recipient_id, text):
    """Gửi tin nhắn văn bản"""
    params = {"access_token": ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    })
    try:
        r = requests.post("https://graph.facebook.com/v17.0/me/messages", params=params, headers=headers, data=data)
        if r.status_code != 200:
            print(f"Lỗi gửi tin: {r.text}")
    except Exception as e:
        print(f"Lỗi kết nối: {e}")

def send_image(recipient_id, image_url):
    """Gửi ảnh"""
    params = {"access_token": ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "image",
                "payload": {"url": image_url, "is_reusable": True}
            }
        }
    })
    try:
        requests.post("https://graph.facebook.com/v17.0/me/messages", params=params, headers=headers, data=data)
    except:
        pass

# ================= XỬ LÝ LỆNH =================

def handle_ai_command(user_id, command, args):
    response_text = ""
    try:
        if command == "/help":
            response_text = "🤖 MENU: /nhac, /time, /thptqg, /wiki, /gg, /code, /updt, /meme, /tarot, /anime, /kbb"

        elif command == "/nhac":
            if not args:
                response_text = "🎶 Nhạc: https://www.youtube.com/watch?v=k5mX3NkA7jM"
            else:
                q = "+".join(args)
                response_text = f"🔎 Tìm nhạc: https://www.youtube.com/results?search_query={q}"

        elif command == "/time":
            now = datetime.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
            response_text = now.strftime("🕒 %H:%M:%S - %d/%m/%Y")

        elif command == "/thptqg":
            days = (datetime.datetime(2026, 6, 12) - datetime.datetime.now()).days
            response_text = f"⏳ Còn {days} ngày tới THPTQG 2026!"

        elif command == "/wiki":
            try:
                response_text = wikipedia.summary(" ".join(args), sentences=2)
            except:
                response_text = "Không tìm thấy trên Wiki."

        elif command == "/gg":
            try:
                res = list(search(" ".join(args), num_results=1, advanced=True))
                if res: response_text = f"{res[0].title}\n{res[0].url}"
                else: response_text = "Không có kết quả."
            except:
                response_text = "Lỗi Google."

        elif command == "/code":
            g = args[0].lower() if args else ""
            codes = GAME_CODES.get(g, ["Nhập tên game: genshin, hsr..."])
            response_text = "\n".join(codes)

        elif command == "/meme":
            try:
                r = requests.get("https://meme-api.com/gimme/animememes").json()
                send_image(user_id, r.get("url"))
                return
            except:
                response_text = "Lỗi meme."

        elif command == "/tarot":
            card = random.choice(TAROT_CARDS)
            response_text = f"🔮 {card['name']}: {card['meaning']}"

        elif command == "/anime":
            animes = ["Naruto", "One Piece", "Bleach"]
            response_text = f"🎬 Anime: {random.choice(animes)}"

        elif command == "/kbb":
            kbb_state[user_id] = "WAITING"
            response_text = "✊✌️✋ Đã úp bài. Bạn chọn: kéo, búa, bao?"

        else:
            response_text = "Lệnh sai. Gõ /help."

    except Exception as e:
        response_text = f"Lỗi: {str(e)}"

    send_message(user_id, response_text)

def handle_kbb_logic(user_id, text):
    choices = ['kéo', 'búa', 'bao']
    if text not in choices: return False
    
    bot = random.choice(choices)
    if text == bot: res = "Hòa!"
    elif (text=='kéo' and bot=='bao') or (text=='búa' and bot=='kéo') or (text=='bao' and bot=='búa'):
        res = "Bạn thắng!"
    else: res = "Bot thắng!"
    
    send_message(user_id, f"📦 Bot ra {bot.upper()}. Kết quả: {res}")
    del kbb_state[user_id]
    return True

# ================= SERVER WEBHOOK =================

@app.route("/", methods=['GET'])
def verify_webhook():
    """Xác minh Webhook"""
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Sai Token", 403

@app.route("/", methods=['POST'])
def webhook_handler():
    """Nhận tin nhắn"""
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data["entry"]:
            for event in entry["messaging"]:
                if "message" in event:
                    sender_id = event["sender"]["id"]
                    
                    # Xử lý ảnh
                    if "attachments" in event["message"]:
                        send_message(sender_id, "Đã nhận ảnh.")
                        return "ok", 200

                    # Xử lý text
                    if "text" in event["message"]:
                        text = event["message"]["text"].strip().lower()

                        if sender_id in kbb_state:
                            if handle_kbb_logic(sender_id, text): continue

                        if text.startswith("/"):
                            parts = text.split()
                            handle_ai_command(sender_id, parts[0], parts[1:])
                        else:
                            send_message(sender_id, "Gõ /help để xem lệnh.")

        return "ok", 200
    return "ok", 404

if __name__ == "__main__":
    app.run(port=5000)
