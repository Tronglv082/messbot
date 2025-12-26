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

# ================= 1. CẤU HÌNH BOT =================
app = Flask(__name__)

# 👇 TOKEN CỦA BẠN (ĐÃ ĐIỀN SẴN)
ACCESS_TOKEN = "EAAJpiB62hRwBQQjVYulX1G6CRANSKLCZBPxF4UhFSZCCebg7uSGCcZAPOti7jjXgUNZCOOfe624MIZBfuCAZCNfaZANLCcKxO3QSomx8mW4xhbOlGzsXwrKDiuO5avRfDnP4DNQdrZB26ni8IZCfqdzjczrbITe2snoFBZBJDUNxxUZC922FvjuIZArIwLN6nqjvwb7HxWNGxIkWawZDZD"
VERIFY_TOKEN = "bot 123"

# Cấu hình ngôn ngữ Wiki
try:
    wikipedia.set_lang("vi")
except:
    pass

# ================= 2. CƠ SỞ DỮ LIỆU & CẤU HÌNH =================

# --- A. MAPPING SỐ THỨ TỰ (1-15) ---
NUMBER_MAP = {
    "1": "/tarot",
    "2": "/nhac",
    "3": "/time",
    "4": "/thptqg",
    "5": "/hld",
    "6": "/wiki",
    "7": "/gg",
    "8": "/kbb",
    "9": "/meme",
    "10": "/anime",
    "11": "/code",
    "12": "/updt",
    "13": "/leak",
    "14": "/banner",
    "15": "/sticker"
}

# --- B. BIẾN TRẠNG THÁI (SESSION) ---
kbb_state = {} 
tarot_sessions = {} 

# --- C. DỮ LIỆU GAME CODE ---
GAME_CODES = {
    "genshin": ["GENSHINGIFT", "CA3BLTURGH9D", "RTJUNRSHTREW", "FATUI"],
    "hsr": ["STARRAILGIFT", "HSRVER10JRL", "MB6N2TVCSQ9F", "POMPOM"],
    "wuwa": ["WUWA2024", "WUTHERINGGIFT", "ROVER123"],
    "wwm": ["WWMVIETNAM", "KIEMHIEP2025"],
    "lq": ["LIENQUAN2025", "GIFTCODELQ", "HPNY2025"],
    "playtogether": ["PT2025", "KAIAISLAND"],
    "bloxfruit": ["SUB2GAMERROBOT", "KITGAMING", "ENYU_IS_PRO"]
}

# --- D. DỮ LIỆU TAROT 78 LÁ ---
MAJORS = {
    0: ("The Fool", "Khởi đầu mới, tự do", "Liều lĩnh, khờ khại"),
    1: ("The Magician", "Kỹ năng, ý chí", "Thao túng, lừa dối"),
    2: ("The High Priestess", "Trực giác, bí ẩn", "Bí mật bị lộ"),
    3: ("The Empress", "Sự trù phú, thiên nhiên", "Phụ thuộc, thiếu thốn"),
    4: ("The Emperor", "Quyền lực, lãnh đạo", "Độc tài, cứng nhắc"),
    5: ("The Hierophant", "Truyền thống, niềm tin", "Giáo điều, đạo đức giả"),
    6: ("The Lovers", "Tình yêu, lựa chọn", "Chia ly, quyết định sai"),
    7: ("The Chariot", "Chiến thắng, ý chí", "Mất phương hướng"),
    8: ("Strength", "Sức mạnh, kiên nhẫn", "Yếu đuối, tự ti"),
    9: ("The Hermit", "Cô đơn, tìm kiếm", "Cô lập, xa lánh"),
    10: ("Wheel of Fortune", "Vận mệnh, may mắn", "Xui xẻo, trì trệ"),
    11: ("Justice", "Công lý, sự thật", "Bất công, dối trá"),
    12: ("The Hanged Man", "Hy sinh, góc nhìn mới", "Bế tắc vô ích"),
    13: ("Death", "Kết thúc, chuyển hóa", "Sợ thay đổi"),
    14: ("Temperance", "Cân bằng, chữa lành", "Mất cân bằng"),
    15: ("The Devil", "Cám dỗ, vật chất", "Giải thoát, cai nghiện"),
    16: ("The Tower", "Sụp đổ, thức tỉnh", "Tai họa, sợ hãi"),
    17: ("The Star", "Hy vọng, niềm tin", "Thất vọng, bi quan"),
    18: ("The Moon", "Ảo tưởng, tiềm thức", "Sự thật phơi bày"),
    19: ("The Sun", "Thành công, niềm vui", "Tạm thời u ám"),
    20: ("Judgement", "Phán xét, tái sinh", "Chối bỏ, hối tiếc"),
    21: ("The World", "Hoàn thành, trọn vẹn", "Dang dở")
}
SUITS = {
    "Wands": ("Gậy", "Lửa - Hành động"),
    "Cups": ("Cốc", "Nước - Cảm xúc"),
    "Swords": ("Kiếm", "Khí - Trí tuệ"),
    "Pentacles": ("Tiền", "Đất - Tiền bạc")
}
RANKS = [
    ("Ace", "Cơ hội mới", "Bỏ lỡ"),
    ("Two", "Cân bằng", "Mất cân bằng"),
    ("Three", "Hợp tác", "Chia rẽ"),
    ("Four", "Ổn định", "Trì trệ"),
    ("Five", "Mất mát", "Hồi phục"),
    ("Six", "Chia sẻ", "Ích kỷ"),
    ("Seven", "Đánh giá", "Ảo tưởng"),
    ("Eight", "Nỗ lực", "Lười biếng"),
    ("Nine", "Độc lập", "Phụ thuộc"),
    ("Ten", "Trọn vẹn", "Tan vỡ"),
    ("Page", "Tin tức", "Tin xấu"),
    ("Knight", "Hành động", "Bốc đồng"),
    ("Queen", "Thấu hiểu", "Lạnh lùng"),
    ("King", "Kiểm soát", "Lạm quyền")
]

SPREADS = {
    "1": {"name": "1 Lá (Thông điệp ngày)", "count": 1, "pos": ["Lời khuyên chính"]},
    "3": {"name": "3 Lá (QK - HT - TL)", "count": 3, "pos": ["Quá khứ", "Hiện tại", "Tương lai"]},
    "5": {"name": "5 Lá (Chi tiết)", "count": 5, "pos": ["Hiện tại", "Thách thức", "Gốc rễ", "Lời khuyên", "Kết quả"]},
    "10": {"name": "Celtic Cross", "count": 10, "pos": ["Hiện tại", "Cản trở", "Tiềm thức", "Quá khứ", "Ý thức", "Tương lai", "Bản thân", "Môi trường", "Hy vọng", "Kết quả"]},
    "12": {"name": "Zodiac", "count": 12, "pos": [f"Tháng {i+1}" for i in range(12)]}
}

# ================= 3. HÀM HỖ TRỢ (API) =================

def send_typing(user_id):
    try:
        requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", 
                      headers={"Content-Type": "application/json"}, 
                      data=json.dumps({"recipient": {"id": user_id}, "sender_action": "typing_on"}))
    except: pass

def send_text(user_id, text):
    try:
        requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", 
                      headers={"Content-Type": "application/json"}, 
                      data=json.dumps({"recipient": {"id": user_id}, "message": {"text": text}}))
    except: pass

def send_image(user_id, url):
    try:
        requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", 
                      headers={"Content-Type": "application/json"}, 
                      data=json.dumps({"recipient": {"id": user_id}, "message": {"attachment": {"type": "image", "payload": {"url": url, "is_reusable": True}}}}))
    except: pass

def send_quick_reply(user_id, text, options):
    q_replies = [{"content_type": "text", "title": t, "payload": p} for t, p in options]
    try:
        requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", 
                      headers={"Content-Type": "application/json"}, 
                      data=json.dumps({"recipient": {"id": user_id}, "messaging_type": "RESPONSE", "message": {"text": text, "quick_replies": q_replies}}))
    except: pass

# ================= 4. LOGIC TÌM KIẾM THÔNG MINH (SMART SEARCH) =================

def smart_search_summary(query, prefix="🔎"):
    """Tìm kiếm Google và trả về Tóm tắt (Tiêu đề + Mô tả) thay vì chỉ link"""
    try:
        # Tìm 1 kết quả tốt nhất
        results = list(search(query, num_results=1, advanced=True))
        if results:
            item = results[0]
            msg = f"{prefix} **KẾT QUẢ TÌM KIẾM:**\n\n"
            msg += f"📌 **{item.title}**\n"
            msg += f"📝 {item.description}\n"
            msg += f"🔗 Chi tiết: {item.url}"
            return msg
        else:
            return f"{prefix} Không tìm thấy thông tin nào mới nhất."
    except Exception as e:
        # Fallback nếu Google chặn IP
        return f"{prefix} Do chính sách bảo mật, mời bạn xem trực tiếp tại đây:\n👉 https://www.google.com/search?q={query.replace(' ', '+')}"

# ================= 5. LOGIC TAROT ENGINE =================

def generate_deck():
    deck = []
    for i, (name, up, rev) in MAJORS.items():
        deck.append({"name": f"{name}", "type": "Major", "up": up, "rev": rev})
    for s_name, (s_vn, s_desc) in SUITS.items():
        for r_name, r_up, r_rev in RANKS:
            deck.append({"name": f"{r_name} of {s_name}", "type": "Minor", "up": f"{r_up} ({s_desc})", "rev": f"{r_rev} ({s_vn})"})
    return deck

def execute_tarot_reading(spread_id, topic="Chung", question=""):
    try:
        deck = generate_deck()
        random.shuffle(deck)
        spread = SPREADS.get(spread_id, SPREADS["3"])
        count = spread["count"]
        drawn = []
        major_c = 0
        for i in range(count):
            if not deck: break
            c = deck.pop()
            is_rev = random.choice([False, False, False, True])
            if c["type"] == "Major": major_c += 1
            drawn.append({
                "pos": spread["pos"][i],
                "name": c["name"],
                "status": "🔻 NGƯỢC" if is_rev else "🔺 XUÔI",
                "meaning": c["rev"] if is_rev else c["up"]
            })
        
        msg = f"🔮 **KẾT QUẢ TAROT: {topic}**\n📜 Spread: {spread['name']}\n➖➖➖➖➖➖\n\n"
        for item in drawn:
            msg += f"📍 **{item['pos']}**: {item['name']} ({item['status']})\n👉 {item['meaning']}\n\n"
        
        msg += "💡 **TỔNG KẾT:** " + ("Định mệnh lớn (Major dominant)." if major_c >= count/2 else "Vấn đề đời thường (Minor dominant).")
        return msg
    except Exception as e: return f"Lỗi Tarot: {str(e)}"

# ================= 6. XỬ LÝ LỆNH (COMMAND HANDLER) =================

def handle_command(user_id, cmd, args):
    cmd = cmd.lower()
    
    # 1. TAROT
    if cmd == "/tarot":
        tarot_sessions[user_id] = {"step": 1}
        options = [("Tình yêu", "Tình yêu"), ("Công việc", "Công việc"), ("Tài chính", "Tài chính")]
        send_quick_reply(user_id, "🔮 **PHÒNG TAROT ONLINE**\nBạn muốn hỏi về chủ đề gì?", options)
    
    # 2. NHẠC
    elif cmd == "/nhac":
        q = " ".join(args) if args else ""
        link = f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}" if q else "https://www.youtube.com/watch?v=k5mX3NkA7jM"
        send_text(user_id, f"🎧 **KẾT QUẢ TÌM NHẠC:**\n👉 {link}")

    # 3. TIME
    elif cmd == "/time":
        now = datetime.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
        send_text(user_id, f"⏰ **GIỜ HIỆN TẠI:**\n{now.strftime('%H:%M:%S')} - Ngày {now.strftime('%d/%m/%Y')}")

    # 4. THPTQG
    elif cmd == "/thptqg":
        days = (datetime.datetime(2026, 6, 25) - datetime.datetime.now()).days
        send_text(user_id, f"⏳ **ĐẾM NGƯỢC THPTQG 2026:**\nCòn {days} ngày nữa! Học đi đừng lười! 📚")

    # 5. NGÀY LỄ (/hld)
    elif cmd == "/hld":
        send_text(user_id, "🎉 **SỰ KIỆN SẮP TỚI:**\n- Tết Nguyên Đán (29/01/2025)\n- Valentine (14/02)\nChuẩn bị tiền đi chơi nhé! 💸")

    # 6. WIKI
    elif cmd == "/wiki":
        if not args: send_text(user_id, "📖 Nhập từ khóa cần tra. Ví dụ: /wiki Hà Nội")
        else:
            try:
                summary = wikipedia.summary(" ".join(args), sentences=3)
                send_text(user_id, f"📚 **WIKIPEDIA:**\n{summary}")
            except: send_text(user_id, "❌ Không tìm thấy trên Wiki.")

    # 7. GOOGLE
    elif cmd == "/gg":
        if not args: send_text(user_id, "🌐 Nhập câu hỏi đi. Ví dụ: /gg Giá vàng hôm nay")
        else:
            res = smart_search_summary(" ".join(args), prefix="🌐")
            send_text(user_id, res)

    # 8. KÉO BÚA BAO
    elif cmd == "/kbb":
        kbb_state[user_id] = "WAITING"
        send_quick_reply(user_id, "✊ **KÉO BÚA BAO**\nBot đã chọn xong. Mời bạn ra tay:", [("✌️", "KEO"), ("✊", "BUA"), ("✋", "BAO")])

    # 9. MEME
    elif cmd == "/meme":
        try:
            r = requests.get("https://meme-api.com/gimme/animememes").json()
            send_image(user_id, r.get("url"))
        except: send_text(user_id, "❌ Lỗi ảnh meme.")

    # 10. ANIME
    elif cmd == "/anime":
        animes = ["Naruto", "One Piece", "Attack on Titan", "Frieren", "Doraemon", "Bleach", "Jujutsu Kaisen"]
        send_text(user_id, f"🎬 **GỢI Ý ANIME:**\nXem bộ này đi hay lắm: **{random.choice(animes)}**")

    # 11. GIFTCODE
    elif cmd == "/code":
        g = args[0].lower() if args else ""
        codes = GAME_CODES.get(g, ["⚠️ Chưa có code game này. (Thử: genshin, hsr, wuwa, lq, bloxfruit)"])
        send_text(user_id, f"🎟️ **GIFTCODE {g.upper()}:**\n" + "\n".join(codes))

    # 12. UPDATE GAME (/updt)
    elif cmd == "/updt":
        if not args: send_text(user_id, "🆕 Nhập tên game (và phiên bản). Ví dụ: `/updt genshin 5.3`")
        else:
            q = " ".join(args)
            query = f"latest update notes {q}"
            res = smart_search_summary(query, prefix="🆕")
            send_text(user_id, f"🔍 Đang tìm thông tin cập nhật cho **{q.upper()}**...\n\n{res}")

    # 13. LEAK GAME (/leak)
    elif cmd == "/leak":
        if not args: send_text(user_id, "🕵️ Nhập tên game cần hóng leak. Ví dụ: `/leak hsr`")
        else:
            q = " ".join(args)
            query = f"latest leaks {q} reddit twitter"
            res = smart_search_summary(query, prefix="🕵️")
            send_text(user_id, f"🕵️ Đang quét các diễn đàn Leak cho **{q.upper()}**...\n\n{res}")

    # 14. BANNER (/banner)
    elif cmd == "/banner":
        if not args: send_text(user_id, "🏷️ Nhập tên game. Ví dụ: `/banner genshin`")
        else:
            q = " ".join(args)
            query = f"current limited banner {q} {datetime.datetime.now().strftime('%B %Y')}"
            res = smart_search_summary(query, prefix="🏷️")
            # Tìm link ảnh banner
            img_search_link = f"https://www.google.com/search?tbm=isch&q={query.replace(' ', '+')}"
            
            msg = f"🏷️ **BANNER HIỆN TẠI: {q.upper()}**\n\n{res}\n\n🖼️ **Xem ảnh banner tại đây:**\n👉 {img_search_link}"
            send_text(user_id, msg)

    # 15. STICKER
    elif cmd == "/sticker":
        send_text(user_id, "🖼️ Hãy gửi kèm một bức ảnh cùng lệnh `/sticker` (hoặc gửi ảnh không cần lệnh) để mình tạo nhãn dán.")

    # MENU CHÍNH
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
            "*(💡 Mẹo: Bạn có thể gõ số 1, 2, 3... thay vì gõ lệnh)*"
        )
        send_text(user_id, menu)
    else:
        send_text(user_id, "Lệnh không đúng. Gõ /help để xem Menu.")

# ================= 7. QUY TRÌNH HỘI THOẠI (TAROT SESSION) =================

def handle_tarot_flow(user_id, text, payload):
    session = tarot_sessions.get(user_id, {"step": 0})
    
    # Anti-Reset: Khôi phục session nếu bị mất
    if payload and "SPREAD_" in payload:
        spread_id = payload.replace("SPREAD_", "")
        send_typing(user_id)
        result = execute_tarot_reading(spread_id, topic="Khôi phục", question="Tự nhẩm")
        send_text(user_id, result)
        if user_id in tarot_sessions: del tarot_sessions[user_id]
        return

    # STEP 1: Topic -> Hỏi câu hỏi
    if session["step"] == 1:
        session["topic"] = payload if payload else text
        session["step"] = 2
        tarot_sessions[user_id] = session
        send_text(user_id, f"Bạn muốn hỏi gì về '{session['topic']}'? (Gõ '.' để bỏ qua)")
        return

    # STEP 2: Câu hỏi -> Hỏi thông tin
    if session["step"] == 2:
        session["question"] = text
        session["step"] = 3
        tarot_sessions[user_id] = session
        send_quick_reply(user_id, "Cho mình biết Cung Hoàng Đạo/Ngày sinh nhé?", [("Bỏ qua", "SKIP_INFO")])
        return

    # STEP 3: Thông tin -> Chọn Spread
    if session["step"] == 3:
        session["info"] = text
        session["step"] = 4
        tarot_sessions[user_id] = session
        options = [("1 Lá", "SPREAD_1"), ("3 Lá", "SPREAD_3"), ("5 Lá", "SPREAD_5"), ("Celtic", "SPREAD_10"), ("Zodiac", "SPREAD_12")]
        send_quick_reply(user_id, "🔹 CHỌN CÁCH TRẢI BÀI:", options)
        return

# ================= 8. MAIN HANDLER (WEBHOOK) =================

@app.route("/", methods=['GET'])
def verify_webhook():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Sai Token", 403

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

                    # 1. Sticker (Ảnh)
                    if attachments and attachments[0]["type"] == "image":
                        send_text(sender_id, "🖼️ Đang tạo sticker...")
                        send_image(sender_id, attachments[0]["payload"]["url"])
                        continue

                    # 2. Số thứ tự (Mapping 1-15)
                    if text in NUMBER_MAP:
                        handle_command(sender_id, NUMBER_MAP[text], [])
                        continue

                    # 3. Tarot Session
                    if sender_id in tarot_sessions or (payload and "SPREAD_" in payload):
                        if text.lower() in ["hủy", "/stop"]:
                            if sender_id in tarot_sessions: del tarot_sessions[sender_id]
                            send_text(sender_id, "Đã hủy.")
                            continue
                        handle_tarot_flow(sender_id, text, payload)
                        continue

                    # 4. Kéo Búa Bao
                    if sender_id in kbb_state and payload:
                        bot = random.choice(["KEO", "BUA", "BAO"])
                        map_i = {"KEO":"✌️", "BUA":"✊", "BAO":"✋"}
                        res = "Hòa! 🤝" if payload==bot else ("Thắng! 🎉" if (payload=="KEO" and bot=="BAO") or (payload=="BUA" and bot=="KEO") or (payload=="BAO" and bot=="BUA") else "Thua! 🐔")
                        send_text(sender_id, f"Bot: {map_i[bot]} | Bạn: {map_i[payload]} => {res}")
                        del kbb_state[sender_id]
                        continue

                    # 5. Lệnh & Chat
                    if text.startswith("/"):
                        parts = text.split()
                        handle_command(sender_id, parts[0], parts[1:])
                    elif text:
                        if text.lower() in ["hi", "alo", "menu"]:
                            handle_command(sender_id, "/help", [])
                        else:
                            send_text(sender_id, "Gõ /help hoặc số 1-15 để dùng lệnh nha.")

        return "ok", 200
    except Exception as e:
        print(f"Error: {e}")
        return "ok", 200

if __name__ == "__main__":
    app.run(port=5000)
