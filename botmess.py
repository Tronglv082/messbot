import os
import sys
import json
import random
import datetime
import pytz
import requests
import wikipedia
from flask import Flask, request

# ================= CẤU HÌNH BOT (Token của bạn) =================
app = Flask(__name__)

ACCESS_TOKEN = "EAAJpiB62hRwBQQjVYulX1G6CRANSKLCZBPxF4UhFSZCCebg7uSGCcZAPOti7jjXgUNZCOOfe624MIZBfuCAZCNfaZANLCcKxO3QSomx8mW4xhbOlGzsXwrKDiuO5avRfDnP4DNQdrZB26ni8IZCfqdzjczrbITe2snoFBZBJDUNxxUZC922FvjuIZArIwLN6nqjvwb7HxWNGxIkWawZDZD"
VERIFY_TOKEN = "bot 123"

# Cấu hình Wiki
try:
    wikipedia.set_lang("vi")
except:
    pass

# Biến lưu trạng thái game
kbb_state = {} 

# ================= DỮ LIỆU TAROT 78 LÁ (NÂNG CẤP) =================

# 1. Ẩn chính (Major Arcana) - 22 lá
MAJORS = {
    0: ("The Fool", "Khởi đầu mới, tự do, ngây thơ", "Liều lĩnh, khờ khạo"),
    1: ("The Magician", "Kỹ năng, ý chí, tập trung", "Thao túng, lừa dối"),
    2: ("The High Priestess", "Trực giác, bí ẩn, tiềm thức", "Bí mật bị lộ, lạnh lùng"),
    3: ("The Empress", "Sự trù phú, thiên nhiên, làm mẹ", "Phụ thuộc, thiếu thốn"),
    4: ("The Emperor", "Quyền lực, cấu trúc, lãnh đạo", "Độc tài, cứng nhắc"),
    5: ("The Hierophant", "Truyền thống, niềm tin", "Giáo điều, đạo đức giả"),
    6: ("The Lovers", "Tình yêu, sự lựa chọn", "Chia ly, quyết định sai"),
    7: ("The Chariot", "Chiến thắng, kiểm soát", "Mất phương hướng, hung hăng"),
    8: ("Strength", "Sức mạnh nội tâm, kiên nhẫn", "Yếu đuối, thiếu tự tin"),
    9: ("The Hermit", "Sự cô đơn, tìm kiếm chân lý", "Cô lập, xa lánh xã hội"),
    10: ("Wheel of Fortune", "Vận mệnh, may mắn", "Xui xẻo, trì trệ"),
    11: ("Justice", "Công lý, sự thật", "Bất công, dối trá"),
    12: ("The Hanged Man", "Hy sinh, góc nhìn mới", "Bế tắc, hy sinh vô ích"),
    13: ("Death", "Kết thúc, chuyển hóa (không hẳn là chết)", "Sợ thay đổi, trì trệ"),
    14: ("Temperance", "Cân bằng, chữa lành", "Mất cân bằng, quá đà"),
    15: ("The Devil", "Cám dỗ, dục vọng, vật chất", "Giải thoát, cai nghiện"),
    16: ("The Tower", "Sụp đổ bất ngờ, thức tỉnh", "Sợ hãi thảm họa"),
    17: ("The Star", "Hy vọng, niềm tin, cảm hứng", "Thất vọng, bi quan"),
    18: ("The Moon", "Ảo tưởng, nỗi sợ, tiềm thức", "Sự thật phơi bày"),
    19: ("The Sun", "Thành công, niềm vui, rực rỡ", "Tạm thời u ám"),
    20: ("Judgement", "Phán xét, tiếng gọi tái sinh", "Chối bỏ, hối tiếc"),
    21: ("The World", "Hoàn thành, trọn vẹn", "Dang dở, thiếu mảnh ghép")
}

# 2. Ẩn phụ (Minor Arcana) - Cấu tạo từ Bộ + Số
SUITS = {
    "Wands": ("Gậy", "Lửa - Hành động, đam mê"),
    "Cups": ("Cốc", "Nước - Cảm xúc, tình yêu"),
    "Swords": ("Kiếm", "Khí - Trí tuệ, xung đột"),
    "Pentacles": ("Tiền", "Đất - Vật chất, sự nghiệp")
}
RANKS = {
    "Ace": ("Cơ hội mới", "Cơ hội bị bỏ lỡ"),
    "Two": ("Cân bằng, lựa chọn", "Mất cân bằng"),
    "Three": ("Hợp tác, ăn mừng", "Chia rẽ, người thứ 3"),
    "Four": ("Ổn định, nghỉ ngơi", "Trì trệ, buồn chán"),
    "Five": ("Mất mát, xung đột", "Hồi phục sau đau thương"),
    "Six": ("Chia sẻ, quá khứ", "Ích kỷ, dính mắc quá khứ"),
    "Seven": ("Đánh giá, ảo tưởng", "Quyết định sáng suốt"),
    "Eight": ("Chăm chỉ, chi tiết", "Lười biếng, làm qua loa"),
    "Nine": ("Độc lập, tự tin", "Phụ thuộc, lo âu"),
    "Ten": ("Trọn vẹn, gánh nặng", "Tan vỡ, giải thoát"),
    "Page": ("Tin tức, người trẻ tuổi", "Tin xấu, non nớt"),
    "Knight": ("Hành động, di chuyển", "Bốc đồng, dừng lại"),
    "Queen": ("Thấu hiểu, nuôi dưỡng", "Lạnh lùng, ghen tuông"),
    "King": ("Kiểm soát, lãnh đạo", "Lạm quyền, yếu kém")
}

# ================= HÀM XỬ LÝ TAROT =================

def generate_tarot_deck():
    """Tạo bộ bài 78 lá"""
    deck = []
    # Thêm Major Arcana
    for i, (name, up, rev) in MAJORS.items():
        deck.append({"name": f"{i}. {name} (Ẩn Chính)", "up": up, "rev": rev, "type": "Major"})
    
    # Thêm Minor Arcana
    for s_name, (s_vn, s_desc) in SUITS.items():
        for r_name, (r_up, r_rev) in RANKS.items():
            full_name = f"{r_name} of {s_name}"
            # Ghép ý nghĩa: Ý nghĩa số + Ý nghĩa bộ
            meaning_up = f"{r_up} trong khía cạnh {s_desc}"
            meaning_rev = f"{r_rev} hoặc tắc nghẽn về {s_desc}"
            deck.append({"name": full_name, "up": meaning_up, "rev": meaning_rev, "type": "Minor"})
    return deck

def draw_tarot_spread(topic="one"):
    """Rút bài theo chủ đề"""
    deck = generate_tarot_deck()
    
    if topic == "3": # 3 lá: Quá khứ - Hiện tại - Tương lai
        cards = random.sample(deck, 3)
        titles = ["Quá khứ", "Hiện tại", "Tương lai"]
    elif topic == "love": # 3 lá: Tình yêu
        cards = random.sample(deck, 3)
        titles = ["Bạn", "Họ (Crush/NY)", "Mối quan hệ"]
    elif topic == "work": # 3 lá: Công việc
        cards = random.sample(deck, 3)
        titles = ["Công việc hiện tại", "Thách thức", "Kết quả"]
    else: # Mặc định 1 lá
        cards = random.sample(deck, 1)
        titles = ["Thông điệp ngẫu nhiên"]

    result_text = ""
    for i, card in enumerate(cards):
        is_reversed = random.choice([True, False]) # Random Ngược/Xuôi
        
        status = "🔻 NGƯỢC" if is_reversed else "🔺 XUÔI"
        meaning = card["rev"] if is_reversed else card["up"]
        
        result_text += f"➖➖➖➖➖➖➖\n"
        result_text += f"🃏 **{titles[i]}:** {card['name']}\n"
        result_text += f"{status}\n"
        result_text += f"👉 *{meaning}*\n"
    
    return result_text

# ================= HÀM GỬI TIN & TIỆN ÍCH KHÁC =================

FUNNY_PREFIXES = [
    "Thưa đại vương, ", "Ối dồi ôi, ", "Tin chuẩn chưa anh? ", 
    "Bot xin thưa rằng: ", "Vâng thưa sếp, ", "Alo alo, kết quả là: "
]

def send_typing(user_id):
    headers = {"Content-Type": "application/json"}
    requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers=headers, data=json.dumps({"recipient": {"id": user_id}, "sender_action": "typing_on"}))

def send_text(user_id, text):
    headers = {"Content-Type": "application/json"}
    requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers=headers, data=json.dumps({"recipient": {"id": user_id}, "message": {"text": text}}))

def send_image(user_id, url):
    headers = {"Content-Type": "application/json"}
    requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers=headers, data=json.dumps({"recipient": {"id": user_id}, "message": {"attachment": {"type": "image", "payload": {"url": url, "is_reusable": True}}}}))

def send_quick_reply(user_id, text, options):
    q_replies = [{"content_type": "text", "title": t, "payload": p} for t, p in options]
    headers = {"Content-Type": "application/json"}
    requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers=headers, data=json.dumps({"recipient": {"id": user_id}, "messaging_type": "RESPONSE", "message": {"text": text, "quick_replies": q_replies}}))

def chat_ai_simulation(text):
    text = text.lower()
    if "buồn" in text: return "Đừng buồn nữa, làm ván /kbb đi! 🥺"
    elif "chán" in text: return "Chán thì gõ /nhac nghe nhạc, hoặc /meme xem ảnh chế!"
    elif "yêu" in text: return "Yêu đương gì tầm này, gõ /tarot love xem tình duyên thế nào!"
    elif "alo" in text or "ê" in text: return "Nghe nè! Gõ /help xem menu nha."
    else: return random.choice(["Gõ /help để xem tôi làm được gì nhé.", "Tôi đang nghe đây...", "Thật thú vị!"])

# ================= XỬ LÝ LỆNH CHÍNH =================

def handle_command(user_id, command, args):
    send_typing(user_id)
    prefix = random.choice(FUNNY_PREFIXES)

    try:
        # 1. MENU
        if command in ["/help", "menu", "hi", "help"]:
            menu = (
                "╔══════════════╗\n"
                "🤖   MENU BOT VIP   🤖\n"
                "╚══════════════╝\n\n"
                "🔮 **TAROT PRO (Mới):**\n"
                "• /tarot : Rút 1 lá ngày\n"
                "• /tarot 3 : Quá khứ - HT - TL\n"
                "• /tarot love : Bói tình yêu\n"
                "• /tarot work : Bói công việc\n\n"
                "🔥 **TIỆN ÍCH:**\n"
                "• /time  : Xem giờ\n"
                "• /wiki <từ> : Tra cứu Wiki\n"
                "• /gg <câu hỏi> : Tra Google\n"
                "• /thptqg : Đếm ngược thi\n\n"
                "🎮 **GIẢI TRÍ:**\n"
                "• /kbb : Kéo Búa Bao\n"
                "• /meme : Ảnh chế\n"
                "• /nhac : Nhạc Chill\n"
                "• /anime : Gợi ý phim\n\n"
                "🎁 **CODE:** /code <game>"
            )
            send_text(user_id, menu)
            return

        # 2. TAROT (NÂNG CẤP)
        elif command == "/tarot":
            topic = args[0].lower() if args else "one"
            if topic in ["3", "ba", "ba lá"]: spread_type = "3"
            elif topic in ["love", "yêu", "tình"]: spread_type = "love"
            elif topic in ["work", "việc", "công"]: spread_type = "work"
            else: spread_type = "one"
            
            result = draw_tarot_spread(spread_type)
            send_text(user_id, f"🔮 {prefix}Kết quả trải bài:\n{result}")

        # 3. GOOGLE (GỬI LINK)
        elif command == "/gg":
            if not args: send_text(user_id, prefix + "Nhập câu hỏi đi sếp. Ví dụ: /gg bao giờ đến Tết")
            else:
                q = " ".join(args).replace(" ", "+")
                link = f"https://www.google.com/search?q={q}"
                send_text(user_id, f"{prefix}Mời sếp bấm vào đây để xem kết quả:\n👉 {link}")

        # 4. KÉO BÚA BAO
        elif command == "/kbb":
            kbb_state[user_id] = "WAITING"
            send_quick_reply(user_id, "✊✌️✋ Bot đã úp bài. Mời ra chiêu:", [("✌️ Kéo", "KEO"), ("✊ Búa", "BUA"), ("✋ Bao", "BAO")])

        # 5. CÁC LỆNH KHÁC
        elif command == "/time":
            now = datetime.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
            send_text(user_id, f"{prefix}Giờ VN: {now.strftime('%H:%M:%S')} - {now.strftime('%d/%m/%Y')}")

        elif command == "/nhac":
            q = "+".join(args) if args else ""
            link = f"https://www.youtube.com/results?search_query={q}" if q else "https://www.youtube.com/watch?v=k5mX3NkA7jM"
            send_text(user_id, f"{prefix}Nhạc của sếp: {link}")

        elif command == "/wiki":
            if not args: send_text(user_id, "Tra gì nói đi? Ví dụ: /wiki Hà Nội")
            else:
                try:
                    summary = wikipedia.summary(" ".join(args), sentences=3)
                    send_text(user_id, f"📚 {prefix}Kết quả Wiki:\n\n{summary}")
                except: send_text(user_id, "Wiki bó tay ca này rồi!")

        elif command == "/meme":
            try:
                r = requests.get("https://meme-api.com/gimme/animememes").json()
                send_image(user_id, r.get("url"))
            except: send_text(user_id, "Lỗi ảnh rồi...")

        elif command == "/code":
            g = args[0].lower() if args else ""
            if "genshin" in g: res = "Genshin: GENSHINGIFT, CA3BLTURGH9D"
            elif "hsr" in g: res = "HSR: STARRAILGIFT, HSRVER10JRL"
            elif "wuwa" in g: res = "WuWa: WUTHERINGGIFT"
            else: res = "Nhập tên game: genshin, hsr, wuwa."
            send_text(user_id, f"🎁 {prefix}{res}")
        
        elif command == "/anime":
            animes = ["Naruto", "One Piece", "Attack on Titan", "Frieren", "Doraemon"]
            send_text(user_id, f"🎬 {prefix}Xem bộ này đi: {random.choice(animes)}")

        elif command == "/thptqg":
            days = (datetime.datetime(2026, 6, 12) - datetime.datetime.now()).days
            send_text(user_id, f"⏳ {prefix}Còn {days} ngày nữa thi THPTQG 2026!")

        else: send_text(user_id, "Lệnh lạ quá. Gõ /help xem menu đi.")

    except Exception as e:
        send_text(user_id, f"⚠️ Lỗi nhẹ: {str(e)}")

# ================= SERVER WEBHOOK =================

@app.route("/", methods=['GET'])
def verify_webhook():
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

                # Xử lý KBB
                if "message" in event and "quick_reply" in event["message"]:
                    payload = event["message"]["quick_reply"]["payload"]
                    if sender_id in kbb_state:
                        bot_c = random.choice(["KEO", "BUA", "BAO"])
                        map_name = {"KEO":"Kéo", "BUA":"Búa", "BAO":"Bao"}
                        if payload == bot_c: res = "Hòa! 🤝"
                        elif (payload=="KEO" and bot_c=="BAO") or (payload=="BUA" and bot_c=="KEO") or (payload=="BAO" and bot_c=="BUA"): res = "Thắng rồi! 🎉"
                        else: res = "Thua nhé! 🐔"
                        send_text(sender_id, f"📦 Bot: {map_name[bot_c]} | Bạn: {map_name[payload]} => {res}")
                        del kbb_state[sender_id]
                    return "ok", 200

                # Xử lý Text
                if "message" in event and "text" in event["message"]:
                    text = event["message"]["text"].strip()
                    if text.startswith("/") or text.lower() in ["menu", "help", "hi"]:
                        parts = text.split()
                        handle_command(sender_id, parts[0].lower(), parts[1:])
                    else:
                        send_typing(sender_id)
                        send_text(sender_id, chat_ai_simulation(text))

        return "ok", 200
    return "ok", 404

if __name__ == "__main__":
    app.run(port=5000)

