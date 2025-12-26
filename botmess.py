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

# Token của bạn
ACCESS_TOKEN = "EAAJpiB62hRwBQYOZBwZCNSFTIgGlnhMCNtZAfsTuHsnFXIcOcg68xQWXfrF9tJ73L9gRaleeXwMRql4SmPPJzStmSZBzvjdrVGeatHqEi2Gw4JnDoZCqmtg1iXcVMIVykP197nZCHbINBvkaxz0fn8sPmMhPDOJgKMZBGLSnMl6Ak5C6SecqkRtcFiYfrkJgMt2RCeJpDaR3QZDZD"
VERIFY_TOKEN = "bot 123"

# Cấu hình ngôn ngữ cho Wikipedia
try:
    wikipedia.set_lang("vi")
except:
    pass

# Biến lưu trạng thái game Kéo Búa Bao
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

# ================= HÀM HỖ TRỢ =================

def send_message(recipient_id, text):
    """Gửi tin nhắn văn bản"""
    params = {"access_token": ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    })
    try:
        requests.post("https://graph.facebook.com/v17.0/me/messages", params=params, headers=headers, data=data)
    except Exception as e:
        print(f"Lỗi gửi tin: {e}")

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
    except Exception as e:
        print(f"Lỗi gửi ảnh: {e}")

# ================= XỬ LÝ LỆNH =================

def handle_ai_command(user_id, command, args):
    response_text = ""
    try:
        # 1. /help
        if command == "/help":
            response_text = (
                "🤖 DANH SÁCH LỆNH:\n"
                "- /nhac [tên]: Nghe nhạc\n"
                "- /time: Xem giờ VN\n"
                "- /thptqg: Đếm ngược thi THPTQG 2026\n"
                "- /wiki <câu hỏi>: Tra cứu Wiki\n"
                "- /gg <câu hỏi>: Tra Google\n"
                "- /code <tên game>: Lấy code (genshin, hsr, wuwa...)\n"
                "- /updt <tên game>: Update game\n"
                "- /meme: Ảnh chế anime\n"
                "- /sticker <ảnh>: Tạo sticker\n"
                "- /tarot <ngày sinh>: Bói bài\n"
                "- /hld: Ngày lễ\n"
                "- /anime [tên]: Gợi ý anime\n"
                "- /kbb: Chơi Kéo Búa Bao"
            )

        # 2. /nhac
        elif command == "/nhac":
            if not args:
                response_text = "🎶 Nhạc ngẫu nhiên: https://www.youtube.com/watch?v=k5mX3NkA7jM"
            else:
                q = " ".join(args).replace(' ', '+')
                response_text = f"🔎 Kết quả tìm kiếm: https://www.youtube.com/results?search_query={q}"

        # 3. /time
        elif command == "/time":
            tz_vn = pytz.timezone('Asia/Ho_Chi_Minh')
            now = datetime.datetime.now(tz_vn)
            response_text = now.strftime("🕒 Bây giờ là: %H:%M:%S - Ngày %d/%m/%Y (GMT+7)")

        # 4. /thptqg
        elif command == "/thptqg":
            target = datetime.datetime(2026, 6, 12)
            now = datetime.datetime.now()
            diff = target - now
            if diff.days > 0:
                response_text = f"⏳ Còn {diff.days} ngày nữa là đến 12/6/2026!"
            else:
                response_text = "Đã qua ngày thi rồi!"

        # 5. /wiki
        elif command == "/wiki":
            if not args:
                response_text = "Nhập từ khóa cần tra. Ví dụ: /wiki Hà Nội"
            else:
                try:
                    summary = wikipedia.summary(" ".join(args), sentences=2)
                    response_text = f"📚 Wiki:\n{summary}"
                except:
                    response_text = "Không tìm thấy thông tin trên Wikipedia."

        # 6. /gg
        elif command == "/gg":
            if not args:
                response_text = "Nhập câu hỏi. Ví dụ: /gg thời tiết"
            else:
                try:
                    res = list(search(" ".join(args), num_results=1, advanced=True))
                    if res:
                        response_text = f"🔍 Google: {res[0].title}\n{res[0].description}\nLink: {res[0].url}"
                    else:
                        response_text = "Không tìm thấy kết quả."
                except:
                    response_text = "Lỗi tìm kiếm Google."

        # 7. /code
        elif command == "/code":
            if not args:
                response_text = "Nhập tên game (genshin, hsr, wuwa, wwm...)"
            else:
                g = args[0].lower()
                codes = GAME_CODES.get(g, ["Chưa có code cho game này."])
                response_text = f"🎁 Code {g.upper()}:\n" + "\n".join(codes)

        # 8. /updt
        elif command == "/updt":
            response_text = "📢 Vui lòng kiểm tra trang chủ game để xem chi tiết bản cập nhật mới nhất."

        # 9. /meme
        elif command == "/meme":
            try:
                r = requests.get("https://meme-api.com/gimme/animememes").json()
                send_image(user_id, r.get("url"))
                return
            except:
                response_text = "Lỗi lấy ảnh meme."

        # 10. /sticker
        elif command == "/sticker":
            response_text = "Hãy gửi kèm một bức ảnh cùng lệnh /sticker."

        # 11. /tarot
        elif command == "/tarot":
            card = random.choice(TAROT_CARDS)
            response_text = f"🔮 Lá bài: {card['name']}\n✨ Ý nghĩa: {card['meaning']}"

        # 12. /hld
        elif command == "/hld":
            response_text = "🎉 Ngày lễ gần nhất: Tết Nguyên Đán."

        # 13. /anime
        elif command == "/anime":
            if not args:
                animes = ["Naruto", "One Piece", "Attack on Titan", "Frieren"]
                response_text = f"🎬 Anime đề xuất: {random.choice(animes)}"
            else:
                name = " ".join(args).replace(' ', '-')
                response_text = f"📺 Link xem: https://vuighe.net/tim-kiem/{name}"

        # 14. /kbb
        elif command == "/kbb":
            kbb_state[user_id] = "WAITING"
            response_text = "✊✌️✋ Bot đã úp bài (🎁).\nBạn chọn: 'kéo', 'búa', hay 'bao'?"

        else:
            response_text = "Lệnh không hợp lệ. Gõ /help để xem menu."

    except Exception as e:
        response_text = f"⚠️ Lỗi xử lý: {str(e)}"

    send_message(user_id, response_text)

def handle_kbb_logic(user_id, user_choice):
    """Logic game Kéo Búa Bao"""
    choices = ['kéo', 'búa', 'bao']
    if user_choice not in choices:
        return False
    
    bot_choice = random.choice(choices)
    if user_choice == bot_choice: result = "Hòa!"
    elif (user_choice=='kéo' and bot_choice=='bao') or \
         (user_choice=='búa' and bot_choice=='kéo') or \
         (user_choice=='bao' and bot_choice=='búa'):
        result = "Bạn thắng! 🎉"
    else:
        result = "Bot thắng! 🤖"
    
    send_message(user_id, f"📦 Bot mở: {bot_choice.upper()}\nBạn chọn: {user_choice.upper()}\n=> {result}")
    del kbb_state[user_id]
    return True

# ================= SERVER WEBHOOK =================

@app.route("/", methods=['GET'])
def verify_webhook():
    """Xác minh Webhook (Chỉ GET)"""
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification token mismatch", 403

@app.route("/", methods=['POST'])
def webhook_handler():
    """Nhận tin nhắn (Chỉ POST)"""
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data["entry"]:
            for event in entry["messaging"]:
                if "message" in event:
                    sender_id = event["sender"]["id"]
                    
                    # 1. Xử lý ảnh (sticker)
                    if "attachments" in event["message"]:
                        for att in event["message"]["attachments"]:
                            if att["type"] == "image":
                                send_message(sender_id, "🖼️ Đang tạo sticker...")
                                send_image(sender_id, att["payload"]["url"])
                                return "ok", 200

                    # 2. Xử lý text
                    if "text" in event["message"]:
                        text = event["message"]["text"].strip().lower()

                        # Check game KBB
                        if sender_id in kbb_state:
                            if handle_kbb_logic(sender_id, text):
                                continue

                        if text.startswith("/"):
                            parts = text.split()
                            handle_ai_command(sender_id, parts[0], parts[1:])
                        else:
                            send_message(sender_id, "Gõ /help để xem menu lệnh.")

        return "EVENT_RECEIVED", 200
    return "Not Found", 404

if __name__ == "__main__":
    app.run(port=5000)
