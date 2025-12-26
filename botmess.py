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

# ================= CẤU HÌNH BOT (ĐÃ THAY TOKEN CỦA BẠN) =================
app = Flask(__name__)

# Token mới nhất bạn cung cấp
ACCESS_TOKEN = "EAAJpiB62hRwBQQjVYulX1G6CRANSKLCZBPxF4UhFSZCCebg7uSGCcZAPOti7jjXgUNZCOOfe624MIZBfuCAZCNfaZANLCcKxO3QSomx8mW4xhbOlGzsXwrKDiuO5avRfDnP4DNQdrZB26ni8IZCfqdzjczrbITe2snoFBZBJDUNxxUZC922FvjuIZArIwLN6nqjvwb7HxWNGxIkWawZDZD"
VERIFY_TOKEN = "bot 123"

# Cấu hình ngôn ngữ Wiki
try:
    wikipedia.set_lang("vi")
except:
    pass

# Biến lưu trạng thái game
kbb_state = {} 

# ================= DỮ LIỆU & TỪ ĐIỂN =================

# Câu dẫn hài hước
FUNNY_PREFIXES = [
    "Thưa đại vương, ", "Ối dồi ôi, ", "Tin chuẩn chưa anh? ", 
    "Bot xin thưa rằng: ", "Đừng bất ngờ nhé, ", "Hệ thống ghi nhận là: ",
    "Vâng thưa sếp, ", "Alo alo, kết quả là: "
]

# Dữ liệu Tarot 78 lá (Rút gọn)
MAJOR_ARCANA = {
    0: ("The Fool", "Khởi đầu mới, tự do, ngây thơ, liều lĩnh."),
    1: ("The Magician", "Kỹ năng, ý chí, sự tập trung."),
    2: ("The High Priestess", "Trực giác, bí ẩn, tiềm thức."),
    3: ("The Empress", "Sự trù phú, thiên nhiên, vẻ đẹp."),
    4: ("The Emperor", "Quyền lực, cấu trúc, lãnh đạo."),
    5: ("The Hierophant", "Truyền thống, niềm tin, tôn giáo."),
    6: ("The Lovers", "Tình yêu, sự hòa hợp, lựa chọn."),
    7: ("The Chariot", "Chiến thắng, kiểm soát, di chuyển."),
    8: ("Strength", "Sức mạnh nội tâm, lòng can đảm."),
    9: ("The Hermit", "Sự cô đơn, tìm kiếm chân lý."),
    10: ("Wheel of Fortune", "Vận mệnh, thay đổi, may mắn."),
    11: ("Justice", "Công lý, sự thật, luật nhân quả."),
    12: ("The Hanged Man", "Hy sinh, góc nhìn mới, chờ đợi."),
    13: ("Death", "Kết thúc, thay đổi lớn (không hẳn là chết)."),
    14: ("Temperance", "Cân bằng, kiên nhẫn, điều độ."),
    15: ("The Devil", "Cám dỗ, ràng buộc, vật chất."),
    16: ("The Tower", "Sụp đổ bất ngờ, tai họa, thức tỉnh."),
    17: ("The Star", "Hy vọng, niềm tin, chữa lành."),
    18: ("The Moon", "Ảo tưởng, nỗi sợ, tiềm thức."),
    19: ("The Sun", "Thành công, niềm vui, năng lượng tích cực."),
    20: ("Judgement", "Phán xét, tái sinh, tiếng gọi."),
    21: ("The World", "Hoàn thành, trọn vẹn, kết thúc hành trình.")
}
SUITS = {"Wands": "Lửa - Hành động", "Cups": "Nước - Cảm xúc", "Swords": "Khí - Trí tuệ", "Pentacles": "Đất - Vật chất"}
RANKS = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"]

# ================= HÀM GỬI TIN =================

def send_typing(user_id):
    """Hiệu ứng đang soạn tin..."""
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"recipient": {"id": user_id}, "sender_action": "typing_on"})
    try:
        requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers=headers, data=data)
    except: pass

def send_text(user_id, text):
    """Gửi tin nhắn text"""
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"recipient": {"id": user_id}, "message": {"text": text}})
    try:
        requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers=headers, data=data)
    except: pass

def send_image(user_id, url):
    """Gửi ảnh"""
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {"id": user_id},
        "message": {"attachment": {"type": "image", "payload": {"url": url, "is_reusable": True}}}
    })
    try:
        requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers=headers, data=data)
    except: pass

def send_quick_reply(user_id, text, options):
    """Gửi nút bấm nhanh"""
    q_replies = [{"content_type": "text", "title": t, "payload": p} for t, p in options]
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {"id": user_id},
        "messaging_type": "RESPONSE",
        "message": {"text": text, "quick_replies": q_replies}
    })
    try:
        requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers=headers, data=data)
    except: pass

# ================= LOGIC XỬ LÝ =================

def get_tarot_card():
    """Rút 1 lá bài chuẩn"""
    if random.random() < 0.3: # 30% ra Ẩn Chính
        idx = random.choice(list(MAJOR_ARCANA.keys()))
        name, mean = MAJOR_ARCANA[idx]
        return f"🃏 ẨN CHÍNH: {name}\n✨ Ý nghĩa: {mean}"
    else: # 70% ra Ẩn Phụ
        suit_en, suit_mean = random.choice(list(SUITS.items()))
        rank = random.choice(RANKS)
        return f"🎴 ẨN PHỤ: {rank} of {suit_en}\n🌊 Nguyên tố: {suit_mean}\n🔑 Lá bài của sự: {rank} (theo số học)"

def chat_ai_simulation(text):
    """Chat tự động khi không dùng lệnh"""
    text = text.lower()
    if "buồn" in text or "khóc" in text:
        return "Thôi đừng buồn nữa, làm ván /kbb với mình cho đời vui lên nào! 🥺"
    elif "chán" in text:
        return "Chán thì gõ /nhac nghe nhạc chill, hoặc /meme xem ảnh chế đi!"
    elif "yêu" in text or "thích" in text:
        return "Yêu đương gì tầm này, lo học hành đi. Gõ /thptqg xem còn bao nhiêu ngày kìa!"
    elif "ngu" in text or "dốt" in text:
        return "Ăn nói xà lơ! Tôi thông minh nhất cái server này đấy. Thử /wiki xem."
    elif "alo" in text or "ê" in text:
        return "Nghe nè! Cần giúp gì thì gõ Menu hoặc /help nha đại ca."
    elif "ngủ" in text:
        return "Chúc ngủ ngon nhé, mơ đẹp đừng mơ thấy bug!"
    else:
        return random.choice([
            "Câu này khó quá, tôi chịu. Bạn thử gõ lệnh khác xem?",
            "Tôi đang lắng nghe đây...",
            "Thật thú vị! Kể tiếp đi.",
            "Bạn nói gì tôi chưa hiểu lắm, nhưng nghe có vẻ uy tín.",
            "Gõ /help để xem tôi làm được gì nhé, chứ chém gió tôi hơi kém."
        ])

def handle_command(user_id, command, args):
    send_typing(user_id)
    prefix = random.choice(FUNNY_PREFIXES) # Thêm mắm muối

    try:
        # 1. MENU
        if command in ["/help", "menu", "hi", "help"]:
            menu = (
                "╔══════════════╗\n"
                "🤖   MENU BOT VIP   🤖\n"
                "╚══════════════╝\n\n"
                "🔥 **TIỆN ÍCH:**\n"
                "1️⃣  /time  : Xem giờ Việt Nam\n"
                "2️⃣  /wiki <từ> : Tra cứu Wikipedia\n"
                "3️⃣  /gg <từ> : Tra Google\n"
                "4️⃣  /thptqg : Đếm ngược ngày thi\n\n"
                "🎮 **GIẢI TRÍ:**\n"
                "5️⃣  /kbb : Kéo Búa Bao (Cực cuốn)\n"
                "6️⃣  /tarot : Bói bài 78 lá chuẩn\n"
                "7️⃣  /meme : Xem ảnh chế Anime\n"
                "8️⃣  /nhac [tên] : Tìm nhạc Chill\n"
                "9️⃣  /anime : Gợi ý phim hay\n\n"
                "🎁 **QUÀ TẶNG:**\n"
                "🔟 /code <game> : Genshin, HSR..."
            )
            send_text(user_id, menu)
            return

        # 2. GOOGLE
        elif command == "/gg":
            if not args:
                send_text(user_id, prefix + "Bạn phải nhập câu hỏi chứ? Ví dụ: /gg giá vàng hôm nay")
            else:
                try:
                    q = " ".join(args)
                    res_iter = search(q, num_results=1, advanced=True)
                    res = next(res_iter, None)
                    if res:
                        send_text(user_id, f"{prefix}Tìm thấy cái này trên Google:\n\n🌐 {res.title}\n👉 {res.url}\n\n📖 {res.description}")
                    else:
                        send_text(user_id, "Tìm đỏ mắt không thấy kết quả nào sếp ơi!")
                except:
                    send_text(user_id, "Google đang bận đi ngủ rồi, thử lại sau nhé.")

        # 3. TAROT
        elif command == "/tarot":
            card_info = get_tarot_card()
            send_text(user_id, f"🔮 {prefix}Vũ trụ gửi tín hiệu:\n\n{card_info}")

        # 4. KÉO BÚA BAO
        elif command == "/kbb":
            kbb_state[user_id] = "WAITING"
            send_quick_reply(user_id, 
                "✊✌️✋ Kèo này căng! Bot đã úp bài.\nMời đại cao thủ ra chiêu:",
                [("✌️ Kéo", "KEO"), ("✊ Búa", "BUA"), ("✋ Bao", "BAO")]
            )

        # 5. THỜI GIAN
        elif command == "/time":
            now = datetime.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
            send_text(user_id, f"{prefix}Bây giờ là: {now.strftime('%H:%M:%S')} (Ngày {now.strftime('%d/%m/%Y')})")

        # 6. NHẠC
        elif command == "/nhac":
            if not args:
                send_text(user_id, f"{prefix}Nghe bài này cho đỡ buồn đời: https://www.youtube.com/watch?v=k5mX3NkA7jM")
            else:
                q = "+".join(args)
                send_text(user_id, f"{prefix}Link nhạc của sếp đây: https://www.youtube.com/results?search_query={q}")

        # 7. WIKI
        elif command == "/wiki":
            if not args:
                send_text(user_id, "Tra gì thì nói đi chứ? Ví dụ: /wiki Sơn Tùng MTP")
            else:
                try:
                    summary = wikipedia.summary(" ".join(args), sentences=3)
                    send_text(user_id, f"📚 {prefix}Kiến thức này đã được tiếp thu:\n\n{summary}")
                except:
                    send_text(user_id, "Ca này khó, Wiki cũng bó tay rồi!")

        # 8. MEME
        elif command == "/meme":
            try:
                r = requests.get("https://meme-api.com/gimme/animememes").json()
                send_image(user_id, r.get("url"))
            except:
                send_text(user_id, "Lỗi load ảnh rồi, quê quá...")

        # 9. CODE GAME
        elif command == "/code":
            g = args[0].lower() if args else ""
            if "genshin" in g: res = "Genshin Impact:\n🎁 GENSHINGIFT\n🎁 CA3BLTURGH9D"
            elif "hsr" in g: res = "Honkai Star Rail:\n🎁 STARRAILGIFT\n🎁 HSRVER10JRL"
            elif "wuwa" in g: res = "Wuthering Waves:\n🎁 WUTHERINGGIFT"
            else: res = "Game này chưa có code, hoặc nhập sai tên rồi (genshin, hsr, wuwa)."
            send_text(user_id, f"🎁 {prefix}{res}")
        
        # 10. ANIME
        elif command == "/anime":
            animes = ["Naruto", "One Piece", "Attack on Titan", "Frieren", "Doraemon", "Bleach"]
            send_text(user_id, f"🎬 {prefix}Cày bộ này đi hay lắm: {random.choice(animes)}")

        # 11. THPTQG
        elif command == "/thptqg":
            days = (datetime.datetime(2026, 6, 12) - datetime.datetime.now()).days
            send_text(user_id, f"⏳ {prefix}Chỉ còn {days} ngày nữa là thi THPTQG 2026. Học đi đừng lười!")

        # LỆNH LẠ
        else:
            send_text(user_id, "Lệnh này lạ quá, tôi chưa học. Gõ /help để xem menu nhé.")

    except Exception as e:
        send_text(user_id, f"⚠️ Bot bị sặc nước rồi: {str(e)}")

# ================= SERVER WEBHOOK =================

@app.route("/", methods=['GET'])
def verify_webhook():
    # Xác thực với Verify Token: bot 123
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Sai Token", 403

@app.route("/", methods=['POST'])
def webhook_handler():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data["entry"]:
            for event in entry["messaging"]:
                sender_id = event["sender"]["id"]

                # 1. Xử lý Quick Reply (Game KBB)
                if "message" in event and "quick_reply" in event["message"]:
                    payload = event["message"]["quick_reply"]["payload"]
                    if sender_id in kbb_state:
                        bot_c = random.choice(["KEO", "BUA", "BAO"])
                        map_name = {"KEO":"Kéo", "BUA":"Búa", "BAO":"Bao"}
                        
                        if payload == bot_c: res = "Hòa rồi! 🤝"
                        elif (payload=="KEO" and bot_c=="BAO") or (payload=="BUA" and bot_c=="KEO") or (payload=="BAO" and bot_c=="BUA"):
                            res = "Bạn thắng! Ghê đấy 🎉"
                        else: res = "Bot thắng! Gà quá 🐔"
                        
                        send_text(sender_id, f"📦 Bot ra: {map_name[bot_c]}\n👉 Bạn chọn: {map_name[payload]}\n=> {res}")
                        del kbb_state[sender_id]
                    return "ok", 200

                # 2. Xử lý Tin nhắn Text
                if "message" in event and "text" in event["message"]:
                    text = event["message"]["text"].strip()
                    
                    if text.startswith("/") or text.lower() in ["menu", "help", "hi", "chào"]:
                        parts = text.split()
                        cmd = parts[0].lower()
                        args = parts[1:]
                        handle_command(sender_id, cmd, args)
                    else:
                        send_typing(sender_id)
                        reply = chat_ai_simulation(text)
                        send_text(sender_id, reply)

        return "ok", 200
    return "ok", 404

if __name__ == "__main__":
    app.run(port=5000)

