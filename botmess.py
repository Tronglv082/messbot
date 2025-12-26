import os
import sys
import json
import random
import datetime
import pytz
import requests
import wikipedia
from flask import Flask, request

# ================= 1. CẤU HÌNH BOT =================
app = Flask(__name__)

# 👇 TOKEN CỦA BẠN
ACCESS_TOKEN = "EAAJpiB62hRwBQQjVYulX1G6CRANSKLCZBPxF4UhFSZCCebg7uSGCcZAPOti7jjXgUNZCOOfe624MIZBfuCAZCNfaZANLCcKxO3QSomx8mW4xhbOlGzsXwrKDiuO5avRfDnP4DNQdrZB26ni8IZCfqdzjczrbITe2snoFBZBJDUNxxUZC922FvjuIZArIwLN6nqjvwb7HxWNGxIkWawZDZD"
VERIFY_TOKEN = "bot 123"

# Cấu hình Wiki tiếng Việt
try:
    wikipedia.set_lang("vi")
except:
    pass

# ================= 2. CƠ SỞ DỮ LIỆU (DATABASE) =================

# --- A. BIẾN LƯU TRẠNG THÁI (SESSION) ---
# Lưu ý: Trên Render Free, biến này sẽ mất khi server restart (khoảng 15p không dùng).
# Code đã thêm logic "bắt lại" session nếu bị mất.
kbb_state = {} 
tarot_sessions = {} 

# --- B. DỮ LIỆU GAME CODE ---
GAME_CODES = {
    "genshin": ["GENSHINGIFT", "CA3BLTURGH9D", "RTJUNRSHTREW", "FATUI"],
    "hsr": ["STARRAILGIFT", "HSRVER10JRL", "MB6N2TVCSQ9F", "POMPOM"],
    "wuwa": ["WUWA2024", "WUTHERINGGIFT", "ROVER123"],
    "wwm": ["WWMVIETNAM", "KIEMHIEP2025"],
    "lq": ["LIENQUAN2025", "GIFTCODELQ", "HPNY2025"],
    "playtogether": ["PT2025", "KAIAISLAND"]
}

# --- C. DỮ LIỆU TAROT 78 LÁ ---
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
    "Knight": ("Hành động", "Bốc đồng"),
    "Queen": ("Thấu hiểu", "Lạnh lùng"),
    "King": ("Kiểm soát", "Lạm quyền")
]

# Các kiểu trải bài
SPREADS = {
    "1": {"name": "1 Lá (Thông điệp ngày)", "count": 1, "pos": ["Lời khuyên chính"]},
    "3": {"name": "3 Lá (QK - HT - TL)", "count": 3, "pos": ["Quá khứ / Nguyên nhân", "Hiện tại / Tình huống", "Tương lai / Kết quả"]},
    "5": {"name": "5 Lá (Giải quyết vấn đề)", "count": 5, "pos": ["Vấn đề hiện tại", "Thách thức", "Gốc rễ", "Lời khuyên", "Kết quả"]},
    "10": {"name": "Celtic Cross (Chi tiết)", "count": 10, "pos": ["Hiện tại", "Cản trở", "Tiềm thức", "Quá khứ", "Ý thức", "Tương lai", "Bản thân", "Môi trường", "Hy vọng", "Kết quả"]},
    "12": {"name": "Zodiac (Tổng quan năm)", "count": 12, "pos": [f"Tháng {i+1}" for i in range(12)]}
}

# ================= 3. HÀM GỬI TIN (API) =================

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

# ================= 4. LOGIC TAROT (XỬ LÝ CHÍNH) =================

def generate_deck():
    """Tạo bộ bài 78 lá"""
    deck = []
    # Major
    for i, (name, up, rev) in MAJORS.items():
        deck.append({"name": f"{name}", "type": "Major", "up": up, "rev": rev})
    # Minor
    for s_name, (s_vn, s_desc) in SUITS.items():
        for r_name, r_up, r_rev in RANKS:
            deck.append({
                "name": f"{r_name} of {s_name}", 
                "type": "Minor", 
                "up": f"{r_up} trong khía cạnh {s_desc}", 
                "rev": f"{r_rev} hoặc tắc nghẽn về {s_vn}"
            })
    return deck

def execute_tarot_reading(user_id, spread_id, topic="Chung", question=""):
    """Thực hiện xào bài, bốc bài và trả về kết quả văn bản"""
    try:
        # 1. Chuẩn bị
        deck = generate_deck()
        random.shuffle(deck)
        
        spread = SPREADS.get(spread_id, SPREADS["3"])
        count = spread["count"]
        
        # 2. Bốc bài
        drawn = []
        major_count = 0
        for i in range(count):
            if not deck: break
            card = deck.pop()
            is_rev = random.choice([False, False, False, True]) # 25% ngược
            
            if card["type"] == "Major": major_count += 1
            
            drawn.append({
                "pos": spread["pos"][i],
                "name": card["name"],
                "status": "🔻 NGƯỢC" if is_rev else "🔺 XUÔI",
                "meaning": card["rev"] if is_rev else card["up"]
            })
        
        # 3. Tạo nội dung trả lời
        msg = f"🔮 **KẾT QUẢ TAROT** 🔮\n"
        msg += f"❤️ Chủ đề: {topic}\n"
        if question: msg += f"❓ Câu hỏi: {question}\n"
        msg += f"📜 Trải bài: {spread['name']}\n"
        msg += "➖➖➖➖➖➖➖➖\n\n"
        
        for item in drawn:
            msg += f"📍 **{item['pos']}**:\n"
            msg += f"   🃏 {item['name']} ({item['status']})\n"
            msg += f"   👉 *{item['meaning']}*\n\n"
            
        msg += "➖➖➖➖➖➖➖➖\n"
        msg += "💡 **LỜI KHUYÊN:**\n"
        if major_count >= count/2:
            msg += "⚠️ Nhiều lá Ẩn Chính xuất hiện: Đây là giai đoạn ĐỊNH MỆNH quan trọng, hãy cân nhắc kỹ.\n"
        else:
            msg += "✅ Nhiều lá Ẩn Phụ: Vấn đề này thuộc đời sống thường nhật, bạn có thể thay đổi kết quả bằng hành động.\n"
            
        return msg
    except Exception as e:
        return f"⚠️ Có lỗi khi trải bài: {str(e)}"

# ================= 5. QUY TRÌNH HỘI THOẠI (STATE MACHINE) =================

def handle_tarot_flow(user_id, text, payload):
    # Lấy session hiện tại hoặc tạo mới
    session = tarot_sessions.get(user_id, {"step": 0})
    
    # CASE ĐẶC BIỆT: Nếu người dùng bấm nút chọn Spread mà bị mất session (do server restart)
    # Ta tự động khôi phục và trả kết quả luôn
    if payload and "SPREAD_" in payload:
        spread_id = payload.replace("SPREAD_", "")
        send_typing(user_id)
        send_text(user_id, f"🔀 Đang xào bài cho trải bài {SPREADS.get(spread_id, {}).get('name', 'Nhanh')}...")
        
        # Thực hiện bói ngay
        result = execute_tarot_reading(user_id, spread_id, topic="Khôi phục", question="Tự nhẩm trong đầu")
        send_text(user_id, result)
        
        if user_id in tarot_sessions: del tarot_sessions[user_id]
        return

    # STEP 1: Chọn Topic -> Hỏi câu hỏi
    if session["step"] == 1:
        session["topic"] = payload if payload else text
        session["step"] = 2
        tarot_sessions[user_id] = session # Cập nhật
        send_text(user_id, f"Bạn muốn hỏi cụ thể gì về '{session['topic']}'? (Hoặc gõ '.' để bỏ qua)")
        return

    # STEP 2: Nhập câu hỏi -> Hỏi thông tin
    if session["step"] == 2:
        session["question"] = text
        session["step"] = 3
        tarot_sessions[user_id] = session
        options = [("Bỏ qua", "SKIP_INFO")]
        send_quick_reply(user_id, "Cho mình biết Cung Hoàng Đạo/Ngày sinh để kết nối tốt hơn nhé? (Bấm Bỏ qua nếu ngại)", options)
        return

    # STEP 3: Nhập Info -> Chọn Spread
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
        send_quick_reply(user_id, "🔹 CHỌN CÁCH TRẢI BÀI:", options)
        return

    # STEP 4: Xử lý chọn Spread -> Kết quả (Đã xử lý ở Case Đặc Biệt trên, nhưng để logic clean thì thêm ở đây)
    if session["step"] == 4:
        # Code không bao giờ chạy tới đây vì nút bấm sẽ lọt vào Case Đặc Biệt ở đầu hàm
        pass

# ================= 6. XỬ LÝ LỆNH (COMMANDS) =================

def handle_command(user_id, cmd, args):
    cmd = cmd.lower()
    
    # 1. TAROT
    if cmd == "/tarot":
        tarot_sessions[user_id] = {"step": 1}
        options = [("Tình yêu", "Tình yêu"), ("Công việc", "Công việc"), ("Tài chính", "Tài chính"), ("Nội tâm", "Nội tâm")]
        send_quick_reply(user_id, "🔮 **PHÒNG TAROT ONLINE**\nBạn muốn hỏi về chủ đề gì?", options)
    
    # 2. MENU / HELP
    elif cmd in ["/help", "menu", "hi", "help"]:
        menu = (
            "🤖 **DANH SÁCH LỆNH BOT**\n"
            "➖➖➖➖➖➖➖➖\n"
            "🔮 **/tarot** : Bói bài 4 bước chuẩn\n"
            "🎵 **/nhac [tên]** : Tìm nhạc Youtube\n"
            "🕒 **/time** : Xem giờ VN\n"
            "⏳ **/thptqg** : Đếm ngược ngày thi\n"
            "📚 **/wiki [từ]** : Tra Wikipedia\n"
            "🔎 **/gg [câu hỏi]** : Link Google\n"
            "🎁 **/code [game]** : Giftcode game\n"
            "✊ **/kbb** : Chơi Kéo Búa Bao\n"
            "🤣 **/meme** : Xem ảnh chế\n"
            "🎬 **/anime** : Gợi ý Anime\n"
            "📅 **/hld** : Ngày lễ sắp tới\n"
            "🖼️ **/sticker** : Gửi ảnh để tạo sticker"
        )
        send_text(user_id, menu)

    # 3. GOOGLE
    elif cmd == "/gg":
        if not args: send_text(user_id, "Nhập câu hỏi đi. Ví dụ: /gg Cách nấu phở")
        else:
            q = " ".join(args).replace(" ", "+")
            send_text(user_id, f"🔎 Kết quả tìm kiếm:\n👉 https://www.google.com/search?q={q}")

    # 4. WIKI
    elif cmd == "/wiki":
        if not args: send_text(user_id, "Tra gì nói đi? Ví dụ: /wiki Bác Hồ")
        else:
            try:
                summary = wikipedia.summary(" ".join(args), sentences=3)
                send_text(user_id, f"📚 Wikipedia:\n{summary}")
            except: send_text(user_id, "Không tìm thấy thông tin.")

    # 5. NHẠC
    elif cmd == "/nhac":
        if not args: send_text(user_id, "🎵 Nhạc ngẫu nhiên: https://www.youtube.com/watch?v=k5mX3NkA7jM")
        else:
            q = "+".join(args)
            send_text(user_id, f"🎵 Link nhạc: https://www.youtube.com/results?search_query={q}")

    # 6. THPTQG
    elif cmd == "/thptqg":
        days = (datetime.datetime(2026, 6, 12) - datetime.datetime.now()).days
        send_text(user_id, f"⏳ Còn {days} ngày nữa là thi THPTQG 2026. Cố lên!")

    # 7. TIME
    elif cmd == "/time":
        now = datetime.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
        send_text(user_id, f"🕒 {now.strftime('%H:%M:%S')} - Ngày {now.strftime('%d/%m/%Y')}")

    # 8. KBB
    elif cmd == "/kbb":
        kbb_state[user_id] = "WAITING"
        send_quick_reply(user_id, "✊✌️✋ Bot đã úp bài. Mời ra chiêu:", [("✌️", "KEO"), ("✊", "BUA"), ("✋", "BAO")])

    # 9. CODE GAME
    elif cmd == "/code":
        g = args[0].lower() if args else ""
        codes = GAME_CODES.get(g, ["Chưa có code game này. Thử: genshin, hsr, wuwa, lq."])
        send_text(user_id, f"🎁 Code {g.upper()}:\n" + "\n".join(codes))

    # 10. ANIME
    elif cmd == "/anime":
        animes = ["Naruto", "One Piece", "Attack on Titan", "Frieren", "Doraemon", "Bleach"]
        send_text(user_id, f"🎬 Xem bộ này đi: {random.choice(animes)}")

    # 11. MEME
    elif cmd == "/meme":
        try:
            r = requests.get("https://meme-api.com/gimme/animememes").json()
            send_image(user_id, r.get("url"))
        except: send_text(user_id, "Lỗi meme.")

    # 12. NGÀY LỄ
    elif cmd == "/hld":
        send_text(user_id, "🎉 Sắp tới: Tết Nguyên Đán (29/01/2025).")

    # 13. UPDATE
    elif cmd == "/updt":
        send_text(user_id, "📢 Kiểm tra trang chủ game để xem update nhé.")
    
    # 14. STICKER
    elif cmd == "/sticker":
        send_text(user_id, "Gửi ảnh kèm lệnh /sticker để mình biến nó thành nhãn dán.")

    # LỆNH LẠ
    else:
        send_text(user_id, "Lệnh không đúng. Gõ /help để xem Menu.")

# ================= 7. ROUTER & MAIN HANDLER =================

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
                    
                    # 1. Lấy dữ liệu (Text, Payload, Attachments)
                    text = event.get("message", {}).get("text", "").strip()
                    payload = event.get("message", {}).get("quick_reply", {}).get("payload")
                    attachments = event.get("message", {}).get("attachments")

                    # --- ƯU TIÊN 1: Xử lý Sticker (Ảnh) ---
                    if attachments and attachments[0]["type"] == "image":
                        send_text(sender_id, "🖼️ Đang tạo sticker...")
                        send_image(sender_id, attachments[0]["payload"]["url"])
                        continue

                    # --- ƯU TIÊN 2: Xử lý Tarot (Session & Recovery) ---
                    # Nếu có session HOẶC người dùng bấm nút SPREAD (khôi phục session)
                    if sender_id in tarot_sessions or (payload and "SPREAD_" in payload):
                        # Nếu gõ lệnh hủy
                        if text.lower() in ["hủy", "/stop", "/cancel"]:
                            if sender_id in tarot_sessions: del tarot_sessions[sender_id]
                            send_text(sender_id, "Đã hủy bói bài.")
                            continue
                        
                        handle_tarot_flow(sender_id, text, payload)
                        continue

                    # --- ƯU TIÊN 3: Xử lý Kéo Búa Bao ---
                    if sender_id in kbb_state and payload:
                        bot = random.choice(["KEO", "BUA", "BAO"])
                        map_i = {"KEO":"✌️", "BUA":"✊", "BAO":"✋"}
                        res = "Hòa! 🤝" if payload==bot else ("Thắng! 🎉" if (payload=="KEO" and bot=="BAO") or (payload=="BUA" and bot=="KEO") or (payload=="BAO" and bot=="BUA") else "Thua! 🐔")
                        send_text(sender_id, f"Bot: {map_i[bot]} | Bạn: {map_i[payload]} => {res}")
                        del kbb_state[sender_id]
                        continue

                    # --- ƯU TIÊN 4: Lệnh & Chat ---
                    if text.startswith("/"):
                        parts = text.split()
                        handle_command(sender_id, parts[0], parts[1:])
                    elif text:
                        # Chat tự động đơn giản
                        if text.lower() in ["hi", "alo", "menu"]:
                            handle_command(sender_id, "/help", [])
                        else:
                            # Không spam "Gõ /help" nữa, chỉ trả lời vui
                            replies = [
                                "Gõ /help để xem mình làm được gì nha.",
                                "Mình đang nghe đây...",
                                "Bạn muốn bói bài không? Gõ /tarot nhé.",
                                "Câu này khó quá, bỏ qua đi :v"
                            ]
                            send_text(sender_id, random.choice(replies))

        return "ok", 200
    except Exception as e:
        print(f"Error: {e}")
        return "error", 200

if __name__ == "__main__":
    app.run(port=5000)

