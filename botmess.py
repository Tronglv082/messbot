import os
import sys
import json
import random
import datetime
import pytz
import requests
import wikipedia
from flask import Flask, request
from duckduckgo_search import DDGS

# ================= 1. CẤU HÌNH BOT =================
app = Flask(__name__)

# 👇 TOKEN CỦA BẠN (ĐÃ ĐIỀN SẴN)
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

# --- D. DỮ LIỆU TAROT CHUYÊN SÂU (Theo yêu cầu mới) ---

# 1. Ẩn Chính (Major Arcana)
MAJORS = {
    0: ("The Fool", "Khởi đầu, tự do, tiềm năng"),
    1: ("The Magician", "Ý chí, sáng tạo, hiện thực hóa"),
    2: ("The High Priestess", "Trực giác, bí mật"),
    3: ("The Empress", "Nuôi dưỡng, tình yêu, trù phú"),
    4: ("The Emperor", "Kỷ luật, lãnh đạo, cấu trúc"),
    5: ("The Hierophant", "Truyền thống, niềm tin"),
    6: ("The Lovers", "Tình yêu, lựa chọn, kết nối"),
    7: ("The Chariot", "Quyết tâm, chiến thắng, ý chí"),
    8: ("Strength", "Nội lực, kiểm soát cảm xúc"),
    9: ("The Hermit", "Nội tâm, chiêm nghiệm, soi rọi"),
    10: ("Wheel of Fortune", "Chu kỳ, vận mệnh, thay đổi"),
    11: ("Justice", "Nhân quả, công bằng, sự thật"),
    12: ("The Hanged Man", "Hy sinh, góc nhìn mới, buông bỏ"),
    13: ("Death", "Kết thúc để tái sinh, chuyển hóa"),
    14: ("Temperance", "Cân bằng, chữa lành, điều độ"),
    15: ("The Devil", "Ràng buộc, cám dỗ, vật chất"),
    16: ("The Tower", "Biến cố, sụp đổ, thức tỉnh"),
    17: ("The Star", "Hy vọng, chữa lành, niềm tin"),
    18: ("The Moon", "Lo lắng, ảo ảnh, tiềm thức"),
    19: ("The Sun", "Thành công, tích cực, niềm vui"),
    20: ("Judgement", "Thức tỉnh, quyết định, kêu gọi"),
    21: ("The World", "Hoàn thành, viên mãn, trọn vẹn")
}

# 2. Ẩn Phụ (Minor Arcana) - Định nghĩa chi tiết từng lá
MINOR_DATA = {
    "Wands": { # Hành động, đam mê
        "Ace": "Khởi đầu", "2": "Lựa chọn", "3": "Mở rộng", "4": "Ổn định", "5": "Cạnh tranh",
        "6": "Thành công", "7": "Bảo vệ", "8": "Nhanh chóng", "9": "Kiên trì", "10": "Gánh nặng",
        "Page": "Tò mò", "Knight": "Bốc đồng", "Queen": "Tự tin", "King": "Lãnh đạo"
    },
    "Cups": { # Cảm xúc, tình yêu
        "Ace": "Tình cảm mới", "2": "Kết nối", "3": "Niềm vui", "4": "Chán nản", "5": "Mất mát",
        "6": "Ký ức", "7": "Ảo tưởng", "8": "Buông bỏ", "9": "Viên mãn", "10": "Hạnh phúc",
        "Page": "Nhạy cảm", "Knight": "Lãng mạn", "Queen": "Thấu cảm", "King": "Kiểm soát cảm xúc"
    },
    "Swords": { # Tư duy, xung đột
        "Ace": "Sự thật", "2": "Do dự", "3": "Đau lòng", "4": "Nghỉ ngơi", "5": "Thất bại",
        "6": "Rời đi", "7": "Gian dối", "8": "Tự trói buộc", "9": "Lo âu", "10": "Sụp đổ",
        "Page": "Quan sát", "Knight": "Hấp tấp", "Queen": "Thẳng thắn", "King": "Lý trí"
    },
    "Pentacles": { # Vật chất, tài chính
        "Ace": "Cơ hội", "2": "Cân bằng", "3": "Hợp tác", "4": "Giữ chặt", "5": "Thiếu thốn",
        "6": "Cho – nhận", "7": "Chờ đợi", "8": "Rèn luyện", "9": "Độc lập", "10": "Sung túc",
        "Page": "Học hỏi", "Knight": "Chăm chỉ", "Queen": "Thực tế", "King": "Thành công"
    }
}

SPREADS = {
    "1": {"name": "1 Lá (Thông điệp nhanh)", "count": 1, "pos": ["Lời khuyên chính"]},
    "3": {"name": "3 Lá (QK - HT - TL)", "count": 3, "pos": ["Quá khứ / Nguyên nhân", "Hiện tại / Tình huống", "Tương lai / Kết quả"]},
    "5": {"name": "5 Lá (Giải quyết vấn đề)", "count": 5, "pos": ["Vấn đề hiện tại", "Thách thức", "Gốc rễ", "Lời khuyên", "Kết quả"]},
    "10": {"name": "Celtic Cross", "count": 10, "pos": ["HT", "Cản trở", "Tiềm thức", "QK", "Ý thức", "TL", "Bản thân", "Môi trường", "Hy vọng", "KQ"]},
    "12": {"name": "Zodiac", "count": 12, "pos": [f"Tháng {i+1}" for i in range(12)]}
}

# ================= 3. HÀM HỖ TRỢ GỬI TIN =================

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

# ================= 5. LOGIC TAROT ENGINE (NÂNG CẤP PRO) =================

def generate_full_deck():
    """Tạo bộ bài 78 lá với ý nghĩa chuẩn xác"""
    deck = []
    # Major Arcana
    for i, (name, meaning) in MAJORS.items():
        deck.append({"name": name, "type": "Major", "suit": "Major", "meaning": meaning})
    
    # Minor Arcana
    for suit, ranks in MINOR_DATA.items():
        for rank, meaning in ranks.items():
            full_name = f"{rank} of {suit}"
            deck.append({"name": full_name, "type": "Minor", "suit": suit, "meaning": meaning})
    return deck

def execute_tarot_reading(user_context):
    """
    GIAI ĐOẠN 3 & 4: Xào bài -> Giải bài
    Logic: Phân tích năng lượng -> Diễn giải liền mạch -> Lời khuyên
    """
    deck = generate_full_deck()
    random.shuffle(deck) # Xào bài
    
    spread_id = user_context.get("spread_id", "3")
    spread = SPREADS.get(spread_id, SPREADS["3"])
    count = spread["count"]
    
    drawn = []
    stats = {"Major": 0, "Wands": 0, "Cups": 0, "Swords": 0, "Pentacles": 0}
    
    # Bốc bài
    for i in range(count):
        if not deck: break
        card = deck.pop()
        is_reversed = random.choice([False, False, False, True]) # 25% bài ngược
        
        # Thống kê năng lượng
        if card["type"] == "Major": stats["Major"] += 1
        else: stats[card["suit"]] += 1
        
        status_text = "Xuôi" if not is_reversed else "Ngược"
        drawn.append({
            "pos": spread["pos"][i],
            "name": card["name"],
            "status": status_text,
            "meaning": card["meaning"],
            "suit": card["suit"],
            "is_reversed": is_reversed
        })
        
    # --- XÂY DỰNG NỘI DUNG TRẢ LỜI ---
    
    # 1. Header & Danh sách bài
    msg = f"🔮 **KẾT QUẢ BỐC {count} LÁ TAROT**\n"
    msg += f"👤 Querent: {user_context.get('info', 'Ẩn danh')}\n"
    msg += f"❤️ Vấn đề: {user_context.get('topic', 'Tổng quan')} - {user_context.get('question', '')}\n\n"
    msg += "Bạn bốc được:\n"
    for idx, item in enumerate(drawn):
        icon = "1️⃣" if idx==0 else "2️⃣" if idx==1 else "3️⃣" if idx==2 else "4️⃣" if idx==3 else "5️⃣" if idx==4 else "🔹"
        msg += f"{icon} {item['name']} – {item['status']}\n"
    
    # 2. Phân tích tổng năng lượng
    msg += "\n🔮 **PHÂN TÍCH TỔNG NĂNG LƯỢNG**\n"
    energy_notes = []
    if stats["Major"] >= count / 2:
        energy_notes.append("Có nhiều lá Ẩn chính → vấn đề mang tính nội tâm, định hướng lâu dài hoặc bài học lớn.")
    if stats["Cups"] >= 2: energy_notes.append("Xuất hiện nhiều Cảm xúc (Cups) → tâm trạng đang chi phối quyết định.")
    if stats["Swords"] >= 2: energy_notes.append("Xuất hiện nhiều Lý trí (Swords) → đang có nhiều suy nghĩ, căng thẳng hoặc xung đột tư duy.")
    if stats["Wands"] >= 2: energy_notes.append("Xuất hiện nhiều Hành động (Wands) → năng lượng muốn làm việc, di chuyển hoặc khao khát.")
    if stats["Pentacles"] >= 2: energy_notes.append("Xuất hiện nhiều Vật chất (Pentacles) → quan tâm đến tiền bạc, sự ổn định thực tế.")
    
    if not energy_notes: energy_notes.append("Năng lượng khá cân bằng, không có yếu tố nào áp đảo quá mức.")
    msg += "\n".join(energy_notes) + "\n"

    # 3. Diễn giải liền mạch (Storytelling)
    msg += "\n🔮 **DIỄN GIẢI LIỀN MẠCH**\n"
    
    # Logic nối văn bản cơ bản (Template based)
    intro_card = drawn[0]
    mid_cards = drawn[1:-1]
    end_card = drawn[-1]
    
    # Mở bài
    story = f"Bài cho thấy hiện tại, năng lượng xoay quanh vấn đề của bạn mang tính chất của **{intro_card['name']}**. "
    if intro_card['is_reversed']:
        story += f"Tuy nhiên, năng lượng này đang bị tắc nghẽn hoặc bạn chưa thực sự đối diện với nó ({intro_card['meaning']}). "
    else:
        story += f"Điều này thể hiện sự {intro_card['meaning']}. "
    
    # Thân bài
    if mid_cards:
        story += "Tiếp theo đó, "
        for c in mid_cards:
            rev_txt = "nhưng lại gặp chút trở ngại hoặc nội tâm chưa thông suốt" if c['is_reversed'] else "và điều này diễn ra khá tự nhiên"
            story += f"sự xuất hiện của **{c['name']}** gợi ý về {c['meaning']}, {rev_txt}. "
            
    # Kết bài
    story += f"Cuối cùng, lá **{end_card['name']}** ({end_card['status']}) khép lại trải bài với thông điệp về {end_card['meaning']}."
    if end_card['is_reversed']:
        story += " Lưu ý rằng kết quả này có thể bị trì hoãn nếu bạn không giải quyết các vấn đề gốc rễ."
    
    msg += story + "\n"

    # 4. Lời khuyên
    msg += "\n🔮 **LỜI KHUYÊN TỪ TAROT**\n"
    msg += "Tarot không quyết định thay bạn, nhưng bài khuyên bạn:\n"
    
    advice_list = []
    # Logic lời khuyên dựa trên lá cuối cùng hoặc bộ chiếm ưu thế
    dominant_suit = max(stats, key=stats.get)
    
    if dominant_suit == "Major":
        advice_list.append("✔️ Hãy nhìn nhận vấn đề này như một bài học lớn của cuộc đời.")
        advice_list.append("✔️ Tin vào trực giác và dòng chảy của số phận.")
    elif dominant_suit == "Swords":
        advice_list.append("✔️ Hãy suy nghĩ thấu đáo nhưng đừng overthinking.")
        advice_list.append("✔️ Cần sự rõ ràng, thẳng thắn trong giao tiếp.")
    elif dominant_suit == "Cups":
        advice_list.append("✔️ Lắng nghe cảm xúc của mình và người khác.")
        advice_list.append("✔️ Đừng để nỗi sợ hay ảo tưởng che mờ lý trí.")
    elif dominant_suit == "Wands":
        advice_list.append("✔️ Đã đến lúc hành động, đừng chần chừ nữa.")
        advice_list.append("✔️ Giữ vững ngọn lửa đam mê nhưng tránh bốc đồng.")
    elif dominant_suit == "Pentacles":
        advice_list.append("✔️ Tập trung vào thực tế, kế hoạch cụ thể.")
        advice_list.append("✔️ Kiên nhẫn, thành quả cần thời gian vun trồng.")
        
    # Thêm lời khuyên từ lá kết quả
    advice_list.append(f"✔️ Hướng tới năng lượng tích cực của {end_card['name']}: {end_card['meaning']}.")
    
    msg += "\n".join(advice_list)
    msg += "\n\n👉 *Khi bạn thay đổi nhận thức, tương lai sẽ thay đổi theo.*"

    return msg

# ================= 6. QUY TRÌNH HỘI THOẠI TAROT (4 GIAI ĐOẠN) =================

def handle_tarot_flow(user_id, text, payload):
    session = tarot_sessions.get(user_id, {"step": 0})
    
    # ANTI-RESET: Khôi phục nếu mất session
    if payload and "SPREAD_" in payload:
        spread_id = payload.replace("SPREAD_", "")
        send_typing(user_id)
        # Giả lập context
        fake_context = {"spread_id": spread_id, "topic": "Khôi phục", "question": "Câu hỏi trong tâm trí", "info": "Ẩn danh"}
        send_text(user_id, f"🔀 Đang xào bài... Tập trung vào câu hỏi nhé...")
        res = execute_tarot_reading(fake_context)
        send_text(user_id, res)
        if user_id in tarot_sessions: del tarot_sessions[user_id]
        return

    # GIAI ĐOẠN 1: THU THẬP THÔNG TIN
    if session["step"] == 1:
        session["topic"] = payload if payload else text
        session["step"] = 2
        tarot_sessions[user_id] = session
        send_text(user_id, f"Bạn muốn hỏi cụ thể gì về '{session['topic']}'? (Gõ '.' để bỏ qua)")
        return

    if session["step"] == 2:
        session["question"] = text
        session["step"] = 3
        tarot_sessions[user_id] = session
        send_quick_reply(user_id, "Cho mình biết Ngày sinh/Cung hoàng đạo nhé?", [("Bỏ qua", "SKIP")])
        return

    # GIAI ĐOẠN 2: CHUẨN BỊ TRẢI BÀI
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
        send_quick_reply(user_id, "🔹 Chọn cách trải bài phù hợp:", options)
        return

# ================= 7. XỬ LÝ LỆNH CHUNG (GIỮ NGUYÊN 15 LỆNH) =================

def handle_command(user_id, cmd, args):
    cmd = cmd.lower()
    
    # 1. TAROT
    if cmd == "/tarot":
        tarot_sessions[user_id] = {"step": 1}
        options = [("Tình yêu", "Tình yêu"), ("Công việc", "Công việc"), ("Tài chính", "Tài chính"), ("Nội tâm", "Nội tâm")]
        send_quick_reply(user_id, "🔮 **PHÒNG TAROT ONLINE**\nBạn muốn hỏi về chủ đề gì?", options)

    # 2. NHẠC
    elif cmd == "/nhac":
        q = " ".join(args) if args else ""
        link = f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}" if q else "https://www.youtube.com/watch?v=k5mX3NkA7jM"
        send_text(user_id, f"🎧 **TÌM NHẠC:** {link}")

    # 3. TIME
    elif cmd == "/time":
        now = datetime.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
        send_text(user_id, f"⏰ **GIỜ VN:** {now.strftime('%H:%M:%S')} - {now.strftime('%d/%m/%Y')}")

    # 4. THPTQG
    elif cmd == "/thptqg":
        days = (datetime.datetime(2026, 6, 25) - datetime.datetime.now()).days
        send_text(user_id, f"⏳ **THPTQG 2026:** Còn {days} ngày!")

    # 5. NGÀY LỄ
    elif cmd == "/hld":
        send_text(user_id, "🎉 **SỰ KIỆN:** Tết Nguyên Đán (29/01), Valentine (14/02).")

    # 6. WIKI
    elif cmd == "/wiki":
        if not args: send_text(user_id, "📖 Tra gì? VD: /wiki Hà Nội")
        else:
            try:
                summary = wikipedia.summary(" ".join(args), sentences=3)
                send_text(user_id, f"📚 **WIKI:**\n{summary}")
            except: send_text(user_id, "❌ Không tìm thấy.")

    # 7. GOOGLE
    elif cmd == "/gg":
        if not args: send_text(user_id, "🌐 Nhập câu hỏi. VD: /gg Giá vàng")
        else:
            res = search_text_summary(" ".join(args))
            send_text(user_id, f"🔎 **KẾT QUẢ:**\n\n{res}")

    # 8. KÉO BÚA BAO
    elif cmd == "/kbb":
        kbb_state[user_id] = "WAITING"
        send_quick_reply(user_id, "✊ **KÉO BÚA BAO**", [("✌️", "KEO"), ("✊", "BUA"), ("✋", "BAO")])

    # 9. MEME
    elif cmd == "/meme":
        try:
            r = requests.get("https://meme-api.com/gimme/animememes").json()
            send_image(user_id, r.get("url"))
        except: send_text(user_id, "❌ Lỗi ảnh.")

    # 10. ANIME
    elif cmd == "/anime":
        animes = ["Naruto", "One Piece", "Attack on Titan", "Frieren", "Doraemon"]
        send_text(user_id, f"🎬 **GỢI Ý:** {random.choice(animes)}")

    # 11. GIFTCODE
    elif cmd == "/code":
        g = args[0].lower() if args else ""
        codes = GAME_CODES.get(g, ["⚠️ Chưa có code."])
        send_text(user_id, f"🎟️ **CODE {g.upper()}:**\n" + "\n".join(codes))

    # 12. UPDATE GAME
    elif cmd == "/updt":
        if not args: send_text(user_id, "🆕 Nhập tên game. VD: `/updt genshin 5.3`")
        else:
            q = " ".join(args)
            send_typing(user_id)
            res = search_text_summary(f"{q} latest update patch notes summary")
            send_text(user_id, f"🆕 **UPDATE {q.upper()}:**\n\n{res}")

    # 13. LEAK GAME
    elif cmd == "/leak":
        if not args: send_text(user_id, "🕵️ Nhập tên game. VD: `/leak hsr`")
        else:
            q = " ".join(args)
            send_typing(user_id)
            res = search_text_summary(f"{q} latest leaks rumors reddit")
            send_text(user_id, f"🕵️ **LEAK {q.upper()}:**\n\n{res}")

    # 14. BANNER
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

    # 15. STICKER
    elif cmd == "/sticker":
        send_text(user_id, "🖼️ Gửi ảnh vào đây để tạo sticker.")

    # MENU CHÍNH
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
