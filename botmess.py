import os
import sys
import json
import random
import datetime
import pytz
import requests
import wikipedia
import time
from flask import Flask, request
from duckduckgo_search import DDGS

# ================= 1. CẤU HÌNH BOT =================
app = Flask(__name__)

# 👇 TOKEN CỦA BẠN
ACCESS_TOKEN = "EAAJpiB62hRwBQQjVYulX1G6CRANSKLCZBPxF4UhFSZCCebg7uSGCcZAPOti7jjXgUNZCOOfe624MIZBfuCAZCNfaZANLCcKxO3QSomx8mW4xhbOlGzsXwrKDiuO5avRfDnP4DNQdrZB26ni8IZCfqdzjczrbITe2snoFBZBJDUNxxUZC922FvjuIZArIwLN6nqjvwb7HxWNGxIkWawZDZD"
VERIFY_TOKEN = "bot 123"

# Cấu hình Wiki
try: wikipedia.set_lang("vi")
except: pass

# ================= 2. CƠ SỞ DỮ LIỆU & CẤU HÌNH =================

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

# --- D. DỮ LIỆU TAROT 78 LÁ CHUẨN ---
MAJORS = {
    0: ("The Fool", "Khởi đầu mới, tự do, liều lĩnh", "Ngây thơ, rủi ro, khởi đầu sai"),
    1: ("The Magician", "Kỹ năng, ý chí, hành động", "Thao túng, lừa dối, trì hoãn"),
    2: ("The High Priestess", "Trực giác, bí ẩn, tiềm thức", "Bí mật bị lộ, kìm nén cảm xúc"),
    3: ("The Empress", "Trù phú, thiên nhiên, làm mẹ", "Phụ thuộc, thiếu thốn, cằn cỗi"),
    4: ("The Emperor", "Quyền lực, cấu trúc, lãnh đạo", "Độc tài, cứng nhắc, thiếu kỷ luật"),
    5: ("The Hierophant", "Truyền thống, niềm tin", "Giáo điều, nổi loạn, đạo đức giả"),
    6: ("The Lovers", "Tình yêu, sự lựa chọn", "Mất cân bằng, chia ly, sai lầm"),
    7: ("The Chariot", "Chiến thắng, kiểm soát", "Mất phương hướng, hung hăng"),
    8: ("Strength", "Sức mạnh nội tâm, kiên nhẫn", "Yếu đuối, thiếu tự tin"),
    9: ("The Hermit", "Cô đơn, tìm kiếm chân lý", "Cô lập, hoang tưởng"),
    10: ("Wheel of Fortune", "Vận mệnh, thay đổi tích cực", "Xui xẻo, kháng cự thay đổi"),
    11: ("Justice", "Công lý, sự thật, nhân quả", "Bất công, dối trá, thiên vị"),
    12: ("The Hanged Man", "Hy sinh, góc nhìn mới", "Bế tắc, ích kỷ, hy sinh vô ích"),
    13: ("Death", "Kết thúc, chuyển hóa, tái sinh", "Sợ thay đổi, trì trệ"),
    14: ("Temperance", "Cân bằng, điều độ, chữa lành", "Mất cân bằng, xung đột"),
    15: ("The Devil", "Cám dỗ, ràng buộc, vật chất", "Giải thoát, cai nghiện"),
    16: ("The Tower", "Sụp đổ, tai họa, thức tỉnh", "Sợ hãi, trốn tránh thảm họa"),
    17: ("The Star", "Hy vọng, niềm tin, cảm hứng", "Thất vọng, bi quan"),
    18: ("The Moon", "Ảo tưởng, tiềm thức, lo âu", "Sự thật phơi bày, giải tỏa"),
    19: ("The Sun", "Thành công, niềm vui, năng lượng", "Tạm thời u ám, kỳ vọng cao"),
    20: ("Judgement", "Phán xét, tiếng gọi, hồi sinh", "Phủ nhận, hối tiếc"),
    21: ("The World", "Hoàn thành, trọn vẹn", "Chưa hoàn thành, trì hoãn")
}
SUITS = {
    "Wands": ("Gậy", "Lửa - Hành động, đam mê"),
    "Cups": ("Cốc", "Nước - Cảm xúc, tình cảm"),
    "Swords": ("Kiếm", "Khí - Trí tuệ, xung đột"),
    "Pentacles": ("Tiền", "Đất - Vật chất, sự nghiệp")
}
RANKS = [
    ("Ace", "Cơ hội mới", "Bỏ lỡ cơ hội"),
    ("Two", "Cân bằng, lựa chọn", "Mất cân bằng"),
    ("Three", "Hợp tác, phát triển", "Chia rẽ, thiếu hợp tác"),
    ("Four", "Ổn định, nghỉ ngơi", "Trì trệ, buồn chán"),
    ("Five", "Mất mát, xung đột", "Hồi phục sau đau thương"),
    ("Six", "Chia sẻ, hoài niệm", "Ích kỷ, dính mắc quá khứ"),
    ("Seven", "Đánh giá, lựa chọn", "Ảo tưởng, mơ mộng"),
    ("Eight", "Nỗ lực, chi tiết", "Lười biếng, làm qua loa"),
    ("Nine", "Độc lập, thành quả", "Phụ thuộc, lo âu"),
    ("Ten", "Trọn vẹn, gánh nặng", "Tan vỡ, áp lực"),
    ("Page", "Tin tức, học hỏi", "Tin xấu, non nớt"),
    ("Knight", "Hành động nhanh", "Bốc đồng, dừng lại"),
    ("Queen", "Thấu hiểu, nuôi dưỡng", "Lạnh lùng, ghen tuông"),
    ("King", "Kiểm soát, lãnh đạo", "Lạm quyền, yếu kém")
]
SPREADS = {
    "1": {"name": "1 Lá (Thông điệp nhanh)", "count": 1, "pos": ["Lời khuyên chính"]},
    "3": {"name": "3 Lá (QK - HT - TL)", "count": 3, "pos": ["Quá khứ / Nguyên nhân", "Hiện tại / Tình huống", "Tương lai / Kết quả"]},
    "5": {"name": "5 Lá (Giải quyết vấn đề)", "count": 5, "pos": ["Vấn đề hiện tại", "Thách thức", "Gốc rễ", "Lời khuyên", "Kết quả"]},
    "7": {"name": "Horseshoe (7 lá)", "count": 7, "pos": ["Quá khứ", "Hiện tại", "Tương lai gần", "Thái độ", "Môi trường", "Hy vọng", "Kết quả"]},
    "10": {"name": "Celtic Cross (Chi tiết)", "count": 10, "pos": ["Hiện tại", "Cản trở", "Tiềm thức", "Quá khứ", "Ý thức", "Tương lai", "Bản thân", "Môi trường", "Hy vọng", "Kết quả"]},
    "12": {"name": "Zodiac (Tổng quan năm)", "count": 12, "pos": [f"Tháng {i+1}" for i in range(12)]}
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

# ================= 4. CÔNG CỤ TÌM KIẾM =================

def search_text_summary(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=1))
            if results:
                res = results[0]
                return f"📌 **{res['title']}**\n\n📝 {res['body']}\n\n🔗 Nguồn: {res['href']}"
            return "Không tìm thấy thông tin."
    except Exception as e: return f"Lỗi tìm kiếm: {str(e)}"

def search_image_url(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(query, max_results=1))
            return results[0]['image'] if results else None
    except: return None

# ================= 5. LOGIC TAROT ENGINE (4 GIAI ĐOẠN) =================

def generate_deck():
    deck = []
    # Major Arcana
    for i, (name, up, rev) in MAJORS.items():
        deck.append({"name": f"{name} (Ẩn Chính)", "type": "Major", "up": up, "rev": rev})
    # Minor Arcana
    for s_name, (s_vn, s_desc) in SUITS.items():
        for r_name, r_up, r_rev in RANKS:
            deck.append({
                "name": f"{r_name} of {s_name}",
                "type": "Minor",
                "up": f"{r_up} - Năng lượng: {s_desc}",
                "rev": f"{r_rev} - Tắc nghẽn: {s_vn}"
            })
    return deck

def execute_tarot_reading(user_context):
    """GIAI ĐOẠN 3 & 4: Xào bài -> Giải bài"""
    deck = generate_deck()
    random.shuffle(deck) # Xào bài
    
    spread_id = user_context.get("spread_id", "3")
    spread = SPREADS.get(spread_id, SPREADS["3"])
    
    drawn = []
    major_count = 0
    
    for i in range(spread["count"]):
        if not deck: break
        card = deck.pop()
        is_reversed = random.choice([False, False, False, True]) # 25% bài ngược
        
        if card["type"] == "Major": major_count += 1
        
        drawn.append({
            "pos": spread["pos"][i],
            "name": card["name"],
            "status": "🔻 NGƯỢC" if is_reversed else "🔺 XUÔI",
            "meaning": card["rev"] if is_reversed else card["up"]
        })
        
    # TẠO VĂN BẢN KẾT QUẢ (STORYTELLING)
    msg = f"🔮 **KẾT QUẢ TRẢI BÀI TAROT**\n"
    msg += f"👤 Người hỏi: {user_context.get('info', 'Ẩn danh')}\n"
    msg += f"❤️ Vấn đề: {user_context.get('topic')} - {user_context.get('question')}\n"
    msg += f"📜 Kiểu trải bài: {spread['name']}\n"
    msg += "➖➖➖➖➖➖➖➖➖➖\n\n"
    
    for item in drawn:
        msg += f"📍 **{item['pos']}**: {item['name']} ({item['status']})\n"
        msg += f"   👉 *{item['meaning']}*\n\n"
        
    msg += "➖➖➖➖➖➖➖➖➖➖\n"
    msg += "💡 **LỜI KHUYÊN TỔNG HỢP:**\n"
    if major_count >= spread["count"] / 2:
        msg += "⚠️ Nhiều lá Ẩn Chính xuất hiện: Giai đoạn này mang tính ĐỊNH MỆNH và bài học lớn. Hãy cân nhắc kỹ trước khi quyết định.\n"
    else:
        msg += "✅ Nhiều lá Ẩn Phụ: Vấn đề thuộc về đời sống thường nhật. Bạn hoàn toàn có thể thay đổi kết quả bằng hành động cụ thể.\n"
        
    return msg

# ================= 6. QUY TRÌNH HỘI THOẠI TAROT (4 GIAI ĐOẠN) =================

def handle_tarot_flow(user_id, text, payload):
    session = tarot_sessions.get(user_id, {"step": 0})
    
    # ANTI-RESET: Khôi phục nếu mất session giữa chừng
    if payload and "SPREAD_" in payload:
        spread_id = payload.replace("SPREAD_", "")
        send_typing(user_id)
        # Giả lập khôi phục context tối thiểu
        fake_context = {"spread_id": spread_id, "topic": "Khôi phục", "question": "Câu hỏi tâm trí", "info": "Ẩn danh"}
        send_text(user_id, f"🔀 Đang xào bài cho trải bài {SPREADS.get(spread_id, {}).get('name')}... (Tập trung nhé)")
        res = execute_tarot_reading(fake_context)
        send_text(user_id, res)
        if user_id in tarot_sessions: del tarot_sessions[user_id]
        return

    # GIAI ĐOẠN 1: THU THẬP THÔNG TIN
    # B1: Chọn Chủ đề -> Hỏi câu hỏi chi tiết
    if session["step"] == 1:
        session["topic"] = payload if payload else text
        session["step"] = 2
        tarot_sessions[user_id] = session
        send_text(user_id, f"Bạn muốn hỏi cụ thể điều gì về '{session['topic']}'? (Hoặc gõ '.' để bỏ qua)")
        return

    # B2: Nhập câu hỏi -> Hỏi thông tin cá nhân
    if session["step"] == 2:
        session["question"] = text
        session["step"] = 3
        tarot_sessions[user_id] = session
        send_quick_reply(user_id, "Cho mình biết Ngày sinh/Cung hoàng đạo để kết nối năng lượng nhé?", [("Bỏ qua", "SKIP")])
        return

    # GIAI ĐOẠN 2: CHUẨN BỊ TRẢI BÀI
    # B3: Nhập Info -> Chọn Spread
    if session["step"] == 3:
        session["info"] = text
        session["step"] = 4
        tarot_sessions[user_id] = session
        options = [
            ("1 Lá (Nhanh)", "SPREAD_1"),
            ("3 Lá (Cơ bản)", "SPREAD_3"),
            ("5 Lá (Chi tiết)", "SPREAD_5"),
            ("Celtic (10 lá)", "SPREAD_10"),
            ("Zodiac (12 lá)", "SPREAD_12")
        ]
        send_quick_reply(user_id, "🔹 Hãy chọn cách trải bài phù hợp:", options)
        return

    # GIAI ĐOẠN 3 & 4: XÀO BÀI & GIẢI BÀI (Xử lý ở phần Payload phía dưới)

# ================= 7. XỬ LÝ LỆNH CHUNG =================

def handle_command(user_id, cmd, args):
    cmd = cmd.lower()
    
    if cmd == "/tarot":
        tarot_sessions[user_id] = {"step": 1}
        options = [("Tình yêu", "Tình yêu"), ("Công việc", "Công việc"), ("Tài chính", "Tài chính"), ("Nội tâm", "Nội tâm")]
        send_quick_reply(user_id, "🔮 **PHÒNG TAROT ONLINE**\nBạn muốn hỏi về chủ đề gì?", options)

    elif cmd == "/nhac":
        q = " ".join(args) if args else ""
        link = f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}" if q else "https://www.youtube.com/watch?v=k5mX3NkA7jM"
        send_text(user_id, f"🎧 **TÌM NHẠC:** {link}")

    elif cmd == "/time":
        now = datetime.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
        send_text(user_id, f"⏰ **GIỜ VN:** {now.strftime('%H:%M:%S')} - {now.strftime('%d/%m/%Y')}")

    elif cmd == "/thptqg":
        days = (datetime.datetime(2026, 6, 25) - datetime.datetime.now()).days
        send_text(user_id, f"⏳ **THPTQG 2026:** Còn {days} ngày!")

    elif cmd == "/hld":
        send_text(user_id, "🎉 **SỰ KIỆN:** Tết Nguyên Đán (29/01), Valentine (14/02).")

    elif cmd == "/wiki":
        if not args: send_text(user_id, "📖 Tra gì? VD: /wiki Hà Nội")
        else:
            try:
                summary = wikipedia.summary(" ".join(args), sentences=3)
                send_text(user_id, f"📚 **WIKI:**\n{summary}")
            except: send_text(user_id, "❌ Không tìm thấy.")

    elif cmd == "/gg":
        if not args: send_text(user_id, "🌐 Nhập câu hỏi. VD: /gg Giá vàng")
        else:
            res = search_text_summary(" ".join(args))
            send_text(user_id, f"🔎 **KẾT QUẢ:**\n\n{res}")

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
        send_text(user_id, f"🎬 **GỢI Ý:** {random.choice(animes)}")

    elif cmd == "/code":
        g = args[0].lower() if args else ""
        codes = GAME_CODES.get(g, ["⚠️ Chưa có code."])
        send_text(user_id, f"🎟️ **CODE {g.upper()}:**\n" + "\n".join(codes))

    elif cmd == "/updt":
        if not args: send_text(user_id, "🆕 Nhập tên game. VD: `/updt genshin 5.3`")
        else:
            q = " ".join(args)
            send_typing(user_id)
            res = search_text_summary(f"{q} latest update patch notes summary")
            send_text(user_id, f"🆕 **UPDATE {q.upper()}:**\n\n{res}")

    elif cmd == "/leak":
        if not args: send_text(user_id, "🕵️ Nhập tên game. VD: `/leak hsr`")
        else:
            q = " ".join(args)
            send_typing(user_id)
            res = search_text_summary(f"{q} latest leaks rumors reddit")
            send_text(user_id, f"🕵️ **LEAK {q.upper()}:**\n\n{res}")

    elif cmd == "/banner":
        if not args: send_text(user_id, "🏷️ Nhập tên game. VD: `/banner genshin`")
        else:
            q = " ".join(args)
            send_typing(user_id)
            now = datetime.datetime.now().strftime('%B %Y')
            info = search_text_summary(f"current limited banner {q} {now}")
            img = search_image_url(f"{q} current banner {now} official")
            send_text(user_id, f"🏷️ **BANNER:**\n{info}")
            if img: send_image(user_id, img)

    elif cmd == "/sticker":
        send_text(user_id, "🖼️ Gửi ảnh vào đây để tạo sticker.")

    elif cmd in ["/help", "menu", "hi"]:
        menu = (
            "✨➖ 🤖 **DANH SÁCH LỆNH BOT** 🤖➖✨\n"
            "                    Tronglv📸\n"
            "➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
            "    🔮 **TAROT & TÂM LINH**\n"
            "✨ 1./tarot : Bói bài Tarot\n\n"
            "    🎵 **ÂM NHẠC**\n"
            "🎧 2./nhac [tên] : Tìm nhạc Youtube\n\n"
            "    🕒 **THỜI GIAN & SỰ KIỆN**\n"
            "⏰ 3./time : Xem giờ hiện tại\n"
            "⏳ 4./thptqg : Đếm ngược ngày thi\n"
            "🎉 5./hld : Ngày lễ sắp tới\n\n"
            "    📚 **TRA CỨU**\n"
            "📖 6./wiki [từ] : Tra Wikipedia\n"
            "🌐 7./gg [câu hỏi] : Link Google\n\n"
            "    🎮 **GIẢI TRÍ**\n"
            "✊ 8./kbb : Chơi Kéo Búa Bao\n"
            "🤣 9./meme : Xem ảnh chế\n"
            "🎬 10./anime : Gợi ý Anime\n\n"
            "    🎁 **GAME**\n"
            "🎟️ 11./code [game] : Giftcode game\n"
            "🆕 12./updt [game] : Thông tin update\n"
            "🕵️ 13./leak [game] : Tổng hợp leak\n"
            "🏷️ 14./banner [game] : Banner hiện tại\n\n"
            "    🖼️ **HÌNH ẢNH**\n"
            "🖌️ 15./sticker : Gửi ảnh để tạo sticker\n\n"
        )
        send_text(user_id, menu)
    else:
        send_text(user_id, "Lệnh không đúng. Gõ /help để xem Menu.")

# ================= 8. MAIN HANDLER =================

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
                        else: send_text(sender_id, "Gõ /help hoặc số 1-15.")

        return "ok", 200
    except: return "ok", 200

if __name__ == "__main__":
    app.run(port=5000)
