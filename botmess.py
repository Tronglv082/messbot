import os
import sys
import json
import random
import datetime
import pytz
import requests
import wikipedia
from flask import Flask, request
from duckduckgo_search import DDGS # Thư viện tìm kiếm xịn hơn Google Search thường

# ================= 1. CẤU HÌNH BOT =================
app = Flask(__name__)

# 👇 TOKEN CỦA BẠN (GIỮ NGUYÊN)
ACCESS_TOKEN = "EAAJpiB62hRwBQQjVYulX1G6CRANSKLCZBPxF4UhFSZCCebg7uSGCcZAPOti7jjXgUNZCOOfe624MIZBfuCAZCNfaZANLCcKxO3QSomx8mW4xhbOlGzsXwrKDiuO5avRfDnP4DNQdrZB26ni8IZCfqdzjczrbITe2snoFBZBJDUNxxUZC922FvjuIZArIwLN6nqjvwb7HxWNGxIkWawZDZD"
VERIFY_TOKEN = "bot 123"

# Cấu hình Wiki
try: wikipedia.set_lang("vi")
except: pass

# ================= 2. CƠ SỞ DỮ LIỆU =================

# --- A. MAPPING SỐ -> LỆNH ---
NUMBER_MAP = {
    "1": "/tarot", "2": "/nhac", "3": "/time", "4": "/thptqg",
    "5": "/hld", "6": "/wiki", "7": "/gg", "8": "/kbb",
    "9": "/meme", "10": "/anime", "11": "/code",
    "12": "/updt", "13": "/leak", "14": "/banner", "15": "/sticker"
}

# --- B. SESSION ---
kbb_state = {} 
tarot_sessions = {} 

# --- C. GAME CODES ---
GAME_CODES = {
    "genshin": ["GENSHINGIFT", "CA3BLTURGH9D", "FATUI"],
    "hsr": ["STARRAILGIFT", "HSRVER10JRL", "POMPOM"],
    "wuwa": ["WUWA2024", "WUTHERINGGIFT"],
    "lq": ["LIENQUAN2025", "HPNY2025"],
    "bloxfruit": ["SUB2GAMERROBOT", "KITGAMING"]
}

# --- D. TAROT DATA ---
MAJORS = {
    0: ("The Fool", "Khởi đầu mới, tự do", "Liều lĩnh"),
    1: ("The Magician", "Kỹ năng, ý chí", "Thao túng"),
    2: ("The High Priestess", "Trực giác, bí ẩn", "Bí mật"),
    3: ("The Empress", "Trù phú, thiên nhiên", "Thiếu thốn"),
    4: ("The Emperor", "Quyền lực, lãnh đạo", "Độc tài"),
    5: ("The Hierophant", "Truyền thống", "Giáo điều"),
    6: ("The Lovers", "Tình yêu", "Chia ly"),
    7: ("The Chariot", "Chiến thắng", "Thất bại"),
    8: ("Strength", "Sức mạnh", "Yếu đuối"),
    9: ("The Hermit", "Cô đơn", "Cô lập"),
    10: ("Wheel of Fortune", "Vận mệnh", "Xui xẻo"),
    11: ("Justice", "Công lý", "Bất công"),
    12: ("The Hanged Man", "Hy sinh", "Bế tắc"),
    13: ("Death", "Kết thúc", "Trì trệ"),
    14: ("Temperance", "Cân bằng", "Mất cân bằng"),
    15: ("The Devil", "Cám dỗ", "Ràng buộc"),
    16: ("The Tower", "Sụp đổ", "Tai họa"),
    17: ("The Star", "Hy vọng", "Thất vọng"),
    18: ("The Moon", "Ảo tưởng", "Sự thật"),
    19: ("The Sun", "Thành công", "U ám"),
    20: ("Judgement", "Phán xét", "Hối tiếc"),
    21: ("The World", "Hoàn thành", "Dang dở")
}
SUITS = {"Wands": "Gậy/Lửa", "Cups": "Cốc/Nước", "Swords": "Kiếm/Khí", "Pentacles": "Tiền/Đất"}
RANKS = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"]
SPREADS = {
    "1": {"name": "1 Lá", "count": 1, "pos": ["Lời khuyên"]},
    "3": {"name": "3 Lá", "count": 3, "pos": ["Quá khứ", "Hiện tại", "Tương lai"]},
    "5": {"name": "5 Lá", "count": 5, "pos": ["Hiện tại", "Thách thức", "Gốc rễ", "Lời khuyên", "Kết quả"]},
    "10": {"name": "Celtic Cross", "count": 10, "pos": ["HT", "Cản trở", "Tiềm thức", "QK", "Ý thức", "TL", "Bản thân", "Môi trường", "Hy vọng", "KQ"]},
    "12": {"name": "Zodiac", "count": 12, "pos": [f"Tháng {i+1}" for i in range(12)]}
}

# ================= 3. HÀM GỬI TIN =================

def send_typing(user_id):
    try: requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers={"Content-Type": "application/json"}, data=json.dumps({"recipient": {"id": user_id}, "sender_action": "typing_on"}))
    except: pass

def send_text(user_id, text):
    try: requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers={"Content-Type": "application/json"}, data=json.dumps({"recipient": {"id": user_id}, "message": {"text": text}}))
    except: pass

def send_image(user_id, url):
    try: requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers={"Content-Type": "application/json"}, data=json.dumps({"recipient": {"id": user_id}, "message": {"attachment": {"type": "image", "payload": {"url": url, "is_reusable": True}}}}))
    except: pass

def send_quick_reply(user_id, text, options):
    q_replies = [{"content_type": "text", "title": t, "payload": p} for t, p in options]
    try: requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers={"Content-Type": "application/json"}, data=json.dumps({"recipient": {"id": user_id}, "messaging_type": "RESPONSE", "message": {"text": text, "quick_replies": q_replies}}))
    except: pass

# ================= 4. CÔNG CỤ TÌM KIẾM NÂNG CAO (DUCKDUCKGO) =================

def search_text_summary(query):
    """Tìm kiếm và trả về nội dung tóm tắt (Text body)"""
    try:
        with DDGS() as ddgs:
            # Tìm kiếm văn bản
            results = list(ddgs.text(query, max_results=1))
            if results:
                res = results[0]
                return f"📌 **{res['title']}**\n\n📝 {res['body']}\n\n🔗 Nguồn: {res['href']}"
            return "Không tìm thấy thông tin."
    except Exception as e:
        return f"Lỗi tìm kiếm: {str(e)}"

def search_image_url(query):
    """Tìm kiếm và trả về link ảnh trực tiếp"""
    try:
        with DDGS() as ddgs:
            # Tìm kiếm ảnh
            results = list(ddgs.images(query, max_results=1))
            if results:
                return results[0]['image'] # Trả về URL ảnh
            return None
    except:
        return None

# ================= 5. LOGIC XỬ LÝ LỆNH =================

def handle_command(user_id, cmd, args):
    cmd = cmd.lower()
    
    # 1. TAROT
    if cmd == "/tarot":
        tarot_sessions[user_id] = {"step": 1}
        options = [("Tình yêu", "Tình yêu"), ("Công việc", "Công việc")]
        send_quick_reply(user_id, "🔮 **PHÒNG TAROT ONLINE**\nBạn muốn hỏi về chủ đề gì?", options)

    # 12. UPDATE (/updt) - Tóm tắt nội dung
    elif cmd == "/updt":
        if not args: send_text(user_id, "🆕 Nhập tên game. Ví dụ: `/updt genshin 5.3`")
        else:
            q = " ".join(args)
            send_typing(user_id)
            # Tìm kiếm nội dung update mới nhất
            res = search_text_summary(f"{q} latest update patch notes summary")
            send_text(user_id, f"🆕 **THÔNG TIN CẬP NHẬT: {q.upper()}**\n\n{res}")

    # 13. LEAK (/leak) - Tổng hợp tin đồn
    elif cmd == "/leak":
        if not args: send_text(user_id, "🕵️ Nhập tên game. Ví dụ: `/leak hsr`")
        else:
            q = " ".join(args)
            send_typing(user_id)
            res = search_text_summary(f"{q} latest leaks and rumors reddit twitter")
            send_text(user_id, f"🕵️ **TỔNG HỢP LEAK: {q.upper()}**\n\n{res}")

    # 14. BANNER (/banner) - Gửi ẢNH thật
    elif cmd == "/banner":
        if not args: send_text(user_id, "🏷️ Nhập tên game. Ví dụ: `/banner genshin`")
        else:
            q = " ".join(args)
            send_typing(user_id)
            
            # 1. Tìm thông tin text (thời gian banner)
            time_now = datetime.datetime.now().strftime('%B %Y')
            text_info = search_text_summary(f"current limited banner {q} {time_now}")
            
            # 2. Tìm ảnh banner
            img_url = search_image_url(f"{q} current banner {time_now} official")
            
            # Gửi text trước
            send_text(user_id, f"🏷️ **BANNER HIỆN TẠI: {q.upper()}**\n\n{text_info}")
            
            # Gửi ảnh sau (nếu tìm thấy)
            if img_url:
                send_image(user_id, img_url)
            else:
                send_text(user_id, "⚠️ Không tìm thấy ảnh banner chất lượng cao.")

    # 7. GOOGLE (/gg) - Tóm tắt thay vì link
    elif cmd == "/gg":
        if not args: send_text(user_id, "🔎 Nhập câu hỏi. Ví dụ: /gg giá vàng")
        else:
            send_typing(user_id)
            res = search_text_summary(" ".join(args))
            send_text(user_id, f"🔎 **KẾT QUẢ TÌM KIẾM:**\n\n{res}")

    # CÁC LỆNH CƠ BẢN KHÁC (GIỮ NGUYÊN)
    elif cmd == "/nhac":
        q = " ".join(args) if args else ""
        link = f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}" if q else "https://www.youtube.com/watch?v=k5mX3NkA7jM"
        send_text(user_id, f"🎧 **KẾT QUẢ TÌM NHẠC:**\n👉 {link}")

    elif cmd == "/time":
        now = datetime.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
        send_text(user_id, f"⏰ **GIỜ VN:** {now.strftime('%H:%M:%S')} - {now.strftime('%d/%m/%Y')}")

    elif cmd == "/thptqg":
        days = (datetime.datetime(2026, 6, 25) - datetime.datetime.now()).days
        send_text(user_id, f"⏳ **THPTQG 2026:** Còn {days} ngày!")

    elif cmd == "/hld":
        send_text(user_id, "🎉 **SỰ KIỆN:** Tết Nguyên Đán (29/01), Valentine (14/02).")

    elif cmd == "/wiki":
        if not args: send_text(user_id, "📖 Tra gì? Ví dụ: /wiki Hà Nội")
        else:
            try:
                summary = wikipedia.summary(" ".join(args), sentences=3)
                send_text(user_id, f"📚 **WIKI:**\n{summary}")
            except: send_text(user_id, "❌ Không tìm thấy.")

    elif cmd == "/kbb":
        kbb_state[user_id] = "WAITING"
        send_quick_reply(user_id, "✊ **KÉO BÚA BAO**", [("✌️", "KEO"), ("✊", "BUA"), ("✋", "BAO")])

    elif cmd == "/meme":
        try:
            r = requests.get("https://meme-api.com/gimme/animememes").json()
            send_image(user_id, r.get("url"))
        except: send_text(user_id, "❌ Lỗi ảnh.")

    elif cmd == "/anime":
        animes = ["Naruto", "One Piece", "Attack on Titan", "Frieren", "Doraemon"]
        send_text(user_id, f"🎬 **XEM THỬ:** {random.choice(animes)}")

    elif cmd == "/code":
        g = args[0].lower() if args else ""
        codes = GAME_CODES.get(g, ["⚠️ Chưa có code. (Thử: genshin, hsr, wuwa, lq)"])
        send_text(user_id, f"🎟️ **CODE {g.upper()}:**\n" + "\n".join(codes))

    elif cmd == "/sticker":
        send_text(user_id, "🖼️ Gửi ảnh vào đây mình biến thành sticker cho.")

    # MENU CHÍNH (GIAO DIỆN MỚI)
    elif cmd in ["/help", "menu", "hi"]:
        menu = (
            "✨➖ 🤖 DANH SÁCH LỆNH BOT 🤖➖✨\n"
            "                    Tronglv📸\n"
            "➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
            "    🔮 TAROT & TÂM LINH\n"
            "✨ 1./tarot : Bói bài Tarot\n"
            "    🎵 ÂM NHẠC\n"
            "🎧 2./nhac [tên] : Tìm nhạc Youtube\n"
            "    🕒 THỜI GIAN & SỰ KIỆN\n"
            "⏰ 3./time : Xem giờ hiện tại\n"
            "⏳ 4./thptqg : Đếm ngược ngày thi\n"
            "🎉 5./hld : Ngày lễ sắp tới\n"
            "    📚 TRA CỨU\n"
            "📖 6./wiki [từ] : Tra Wikipedia\n"
            "🌐 7./gg [câu hỏi] : Link Google\n"
            "    🎮 GIẢI TRÍ\n"
            "✊ 8./kbb : Chơi Kéo Búa Bao\n"
            "🤣 9./meme : Xem ảnh chế\n"
            "🎬 10./anime : Gợi ý Anime\n"
            "    🎁 GAME\n"
            "🎟️ 11./code [game] : Giftcode game\n"
            "🆕 12./updt [game] : Thông tin update\n"
            "🕵️ 13./leak [game] : Tổng hợp leak\n"
            "🏷️ 14./banner [game] : Banner hiện tại\n"
            "    🖼️ HÌNH ẢNH\n"
            "🖌️ 15./sticker : Gửi ảnh để tạo sticker\n\n"
            "*(💡 Mẹo: Nhắn số thứ tự để dùng lệnh nhanh)*"
        )
        send_text(user_id, menu)
    else:
        send_text(user_id, "Lệnh không đúng. Gõ /help để xem Menu.")

# ================= 6. XỬ LÝ TAROT FLOW =================

def generate_deck():
    deck = []
    for i, (name, up, rev) in MAJORS.items():
        deck.append({"name": name, "type": "Major", "up": up, "rev": rev})
    for s, n in SUITS.items():
        for r, u, v in RANKS:
            deck.append({"name": f"{r} of {s}", "type": "Minor", "up": u, "rev": v})
    return deck

def execute_tarot(spread_id, topic):
    try:
        deck = generate_deck()
        random.shuffle(deck)
        spread = SPREADS.get(spread_id, SPREADS["3"])
        drawn = []
        for i in range(spread["count"]):
            if not deck: break
            c = deck.pop()
            is_rev = random.choice([False, False, True])
            drawn.append(f"📍 **{spread['pos'][i]}**: {c['name']} ({'🔻 Ngược' if is_rev else '🔺 Xuôi'})\n👉 {c['rev'] if is_rev else c['up']}")
        return f"🔮 **TAROT: {topic}**\n\n" + "\n\n".join(drawn)
    except: return "Lỗi Tarot."

def handle_tarot_flow(user_id, text, payload):
    session = tarot_sessions.get(user_id, {"step": 0})
    
    if payload and "SPREAD_" in payload: # Anti-reset
        send_typing(user_id)
        res = execute_tarot(payload.replace("SPREAD_", ""), "Khôi phục")
        send_text(user_id, res)
        if user_id in tarot_sessions: del tarot_sessions[user_id]
        return

    if session["step"] == 1:
        session["topic"] = payload if payload else text
        session["step"] = 2
        tarot_sessions[user_id] = session
        send_text(user_id, f"Hỏi gì về {session['topic']}? (Gõ '.' bỏ qua)")
        return
    
    if session["step"] == 2:
        session["step"] = 3
        tarot_sessions[user_id] = session
        send_quick_reply(user_id, "Ngày sinh/Cung hoàng đạo?", [("Bỏ qua", "SKIP")])
        return

    if session["step"] == 3:
        session["step"] = 4
        tarot_sessions[user_id] = session
        send_quick_reply(user_id, "Chọn trải bài:", [("1 Lá", "SPREAD_1"), ("3 Lá", "SPREAD_3"), ("5 Lá", "SPREAD_5")])
        return

# ================= 7. MAIN ROUTER =================

@app.route("/", methods=['GET'])
def verify_webhook():
    return request.args.get("hub.challenge") if request.args.get("hub.verify_token") == VERIFY_TOKEN else "Error"

@app.route("/", methods=['POST'])
def webhook_handler():
    try:
        data = request.get_json()
        if data.get("object") == "page":
            for entry in data["entry"]:
                for event in entry["messaging"]:
                    sender_id = event["sender"]["id"]
                    text = event.get("message", {}).get("text", "").strip()
                    payload = event.get("message", {}).get("quick_reply", {}).get("payload")
                    attachments = event.get("message", {}).get("attachments")

                    if attachments and attachments[0]["type"] == "image":
                        send_text(sender_id, "🖼️ Đang tạo sticker...")
                        send_image(sender_id, attachments[0]["payload"]["url"])
                        continue

                    # Mapping Số -> Lệnh
                    if text in NUMBER_MAP:
                        handle_command(sender_id, NUMBER_MAP[text], [])
                        continue

                    if sender_id in tarot_sessions or (payload and "SPREAD_" in payload):
                        if text.lower() in ["hủy", "/stop"]:
                            del tarot_sessions[sender_id]
                            send_text(sender_id, "Đã hủy.")
                            continue
                        handle_tarot_flow(sender_id, text, payload)
                        continue

                    if sender_id in kbb_state and payload:
                        b = random.choice(["KEO", "BUA", "BAO"])
                        res = "Hòa" if payload==b else ("Thắng" if (payload=="KEO" and b=="BAO") or (payload=="BUA" and b=="KEO") or (payload=="BAO" and b=="BUA") else "Thua")
                        send_text(sender_id, f"Bot: {b} | Bạn: {payload} => {res}")
                        del kbb_state[sender_id]
                        continue

                    if text.startswith("/"):
                        parts = text.split()
                        handle_command(sender_id, parts[0], parts[1:])
                    elif text:
                        if text.lower() in ["hi", "menu"]: handle_command(sender_id, "/help", [])
                        else: send_text(sender_id, "Gõ /help hoặc số 1-15 để mở Menu.")

        return "ok", 200
    except: return "ok", 200

if __name__ == "__main__":
    app.run(port=5000)

