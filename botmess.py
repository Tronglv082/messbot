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

# 👇 TOKEN CỦA BẠN (ĐÃ ĐIỀN SẴN)
ACCESS_TOKEN = "EAAJpiB62hRwBQQjVYulX1G6CRANSKLCZBPxF4UhFSZCCebg7uSGCcZAPOti7jjXgUNZCOOfe624MIZBfuCAZCNfaZANLCcKxO3QSomx8mW4xhbOlGzsXwrKDiuO5avRfDnP4DNQdrZB26ni8IZCfqdzjczrbITe2snoFBZBJDUNxxUZC922FvjuIZArIwLN6nqjvwb7HxWNGxIkWawZDZD"
VERIFY_TOKEN = "bot 123"

# Cấu hình Wiki
try: wikipedia.set_lang("vi")
except: pass

# ================= 2. CƠ SỞ DỮ LIỆU & CẤU HÌNH =================

# --- A. MAPPING SỐ -> LỆNH ---
NUMBER_MAP = {
    "1": "/tarot", "2": "/baitay", "3": "/nhac", "4": "/time", "5": "/thptqg",
    "6": "/hld", "7": "/wiki", "8": "/gg", "9": "/kbb",
    "10": "/meme", "11": "/anime", "12": "/code",
    "13": "/updt", "14": "/sticker"
}

# --- B. SESSION ---
kbb_state = {} 
tarot_sessions = {} # Dùng chung cho cả Tarot và Bài Tây

# --- C. GAME CODES ---
GAME_CODES = {
    "genshin": ["GENSHINGIFT", "CA3BLTURGH9D", "FATUI"],
    "hsr": ["STARRAILGIFT", "HSRVER10JRL", "POMPOM"],
    "wuwa": ["WUWA2024", "WUTHERINGGIFT"],
    "lq": ["LIENQUAN2025", "HPNY2025"],
    "bloxfruit": ["SUB2GAMERROBOT", "KITGAMING"]
}

# --- D. DỮ LIỆU TAROT 78 LÁ ---
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

MINOR_DATA = {
    "Wands": {"Ace": "Khởi đầu", "2": "Lựa chọn", "3": "Mở rộng", "4": "Ổn định", "5": "Cạnh tranh", "6": "Thành công", "7": "Bảo vệ", "8": "Nhanh chóng", "9": "Kiên trì", "10": "Gánh nặng", "Page": "Tò mò", "Knight": "Bốc đồng", "Queen": "Tự tin", "King": "Lãnh đạo"},
    "Cups": {"Ace": "Tình cảm mới", "2": "Kết nối", "3": "Niềm vui", "4": "Chán nản", "5": "Mất mát", "6": "Ký ức", "7": "Ảo tưởng", "8": "Buông bỏ", "9": "Viên mãn", "10": "Hạnh phúc", "Page": "Nhạy cảm", "Knight": "Lãng mạn", "Queen": "Thấu cảm", "King": "Kiểm soát cảm xúc"},
    "Swords": {"Ace": "Sự thật", "2": "Do dự", "3": "Đau lòng", "4": "Nghỉ ngơi", "5": "Thất bại", "6": "Rời đi", "7": "Gian dối", "8": "Tự trói buộc", "9": "Lo âu", "10": "Sụp đổ", "Page": "Quan sát", "Knight": "Hấp tấp", "Queen": "Thẳng thắn", "King": "Lý trí"},
    "Pentacles": {"Ace": "Cơ hội", "2": "Cân bằng", "3": "Hợp tác", "4": "Giữ chặt", "5": "Thiếu thốn", "6": "Cho – nhận", "7": "Chờ đợi", "8": "Rèn luyện", "9": "Độc lập", "10": "Sung túc", "Page": "Học hỏi", "Knight": "Chăm chỉ", "Queen": "Thực tế", "King": "Thành công"}
}

SPREADS_TAROT = {
    "1": {"name": "1 Lá (Nhanh)", "count": 1, "pos": ["Lời khuyên chính"]},
    "3": {"name": "3 Lá (QK-HT-TL)", "count": 3, "pos": ["Quá khứ", "Hiện tại", "Tương lai"]},
    "5": {"name": "5 Lá (Chi tiết)", "count": 5, "pos": ["Vấn đề", "Thách thức", "Gốc rễ", "Lời khuyên", "Kết quả"]},
    "10": {"name": "Celtic Cross", "count": 10, "pos": ["HT", "Cản trở", "Tiềm thức", "QK", "Ý thức", "TL", "Bản thân", "Môi trường", "Hy vọng", "KQ"]},
    "12": {"name": "Zodiac", "count": 12, "pos": [f"Tháng {i+1}" for i in range(12)]}
}

# --- E. DỮ LIỆU BÀI TÂY 52 LÁ (FULL ABSOLUTE) ---
PLAYING_CARDS_MEANING = {
    "Hearts": { # Cơ: Tình cảm
        "A": "Tình yêu mới, hạnh phúc, gia đình", "K": "Người đàn ông chân thành, tốt bụng", "Q": "Người phụ nữ dịu dàng, đáng tin", "J": "Tin tức tình yêu, người trẻ tuổi",
        "10": "Hạnh phúc viên mãn, cưới hỏi", "9": "Điều ước thành hiện thực", "8": "Hẹn hò, gặp gỡ, giao lưu", "7": "Ghen tuông, ảo tưởng tình cảm",
        "6": "Người cũ quay lại, hoài niệm", "5": "Buồn bã, chia tay, thất vọng", "4": "Ổn định, cam kết lâu dài", "3": "Tình tay ba, sự xen ngang", "2": "Tình yêu đôi lứa, kết đôi"
    },
    "Diamonds": { # Rô: Tiền bạc
        "A": "Cơ hội tài chính mới, giấy tờ quan trọng", "K": "Đàn ông thành đạt, có tiền", "Q": "Phụ nữ giỏi quản lý tiền, thực tế", "J": "Tin tức về tiền bạc, lợi nhuận",
        "10": "Giàu có, thành công lớn, tiền về", "9": "Tự lập tài chính, thoải mái chi tiêu", "8": "Học tập, rèn luyện kỹ năng kiếm tiền", "7": "Rủi ro tài chính, cẩn thận đầu tư",
        "6": "Sự giúp đỡ, vay mượn, từ thiện", "5": "Mất mát tiền bạc, khó khăn tạm thời", "4": "Tiết kiệm, giữ chặt tài sản, ổn định", "3": "Hợp tác làm ăn, đầu tư chung", "2": "Hợp đồng, thỏa thuận tài chính"
    },
    "Clubs": { # Tép: Công việc
        "A": "Khởi đầu công việc mới, dự án mới", "K": "Quyền lực, sếp, người lãnh đạo", "Q": "Thông minh, khéo léo trong giao tiếp", "J": "Người trẻ học việc, nhân viên mới",
        "10": "Thành công lớn trong sự nghiệp, thăng tiến", "9": "Tham vọng, áp lực công việc cao", "8": "Tin tức nhanh, di chuyển, công tác", "7": "Tranh chấp, mâu thuẫn đồng nghiệp",
        "6": "Cơ hội phát triển, được ghi nhận", "5": "Thay đổi môi trường, thử thách mới", "4": "Nền tảng công việc ổn định, chắc chắn", "3": "Cân nhắc lựa chọn hướng đi", "2": "Hợp tác, hỗ trợ trong công việc"
    },
    "Spades": { # Bích: Thử thách
        "A": "Kết thúc để khởi đầu lại, quyết định dứt khoát", "K": "Đàn ông nghiêm khắc, pháp luật", "Q": "Phụ nữ sắc sảo, cô độc hoặc góa phụ", "J": "Tin xấu, tiểu nhân, gián điệp",
        "10": "Gánh nặng, xui xẻo, áp lực cực đại", "9": "Lo âu, mất ngủ, đau khổ tâm lý", "8": "Trở ngại bất ngờ, bị chặn đường", "7": "Phản bội, lừa dối, cẩn thận sau lưng",
        "6": "Rời bỏ, đi xa, trốn tránh", "5": "Thất bại, mất mát, đổ vỡ", "4": "Trì hoãn, bệnh tật, mệt mỏi", "3": "Chia ly, đau lòng, rạn nứt", "2": "Mâu thuẫn, xung đột trực diện"
    }
}

SPREADS_PLAYING = {
    "3": {"name": "3 Lá (QK-HT-TL)", "count": 3, "pos": ["Quá khứ ảnh hưởng", "Hiện tại", "Xu hướng tương lai"]},
    "5": {"name": "5 Lá (Tổng quan)", "count": 5, "pos": ["Vấn đề chính", "Nguyên nhân", "Yếu tố tiềm ẩn", "Lời khuyên", "Kết quả"]},
    "7": {"name": "7 Lá (Tình duyên)", "count": 7, "pos": ["Bạn", "Đối phương", "Cảm xúc bạn", "Cảm xúc họ", "Trở ngại 1", "Trở ngại 2", "Kết quả"]}
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

# ================= 5. LOGIC TAROT ENGINE =================

def generate_tarot_deck():
    deck = []
    for i, (name, meaning) in MAJORS.items():
        deck.append({"name": f"{name} (Ẩn Chính)", "type": "Major", "suit": "Major", "meaning": meaning})
    for suit, ranks in MINOR_DATA.items():
        for rank, meaning in ranks.items():
            full_name = f"{rank} of {suit}"
            deck.append({"name": full_name, "type": "Minor", "suit": suit, "meaning": meaning})
    return deck

def execute_tarot_reading(user_context):
    deck = generate_tarot_deck()
    random.shuffle(deck)
    spread = SPREADS_TAROT.get(user_context.get("spread_id", "3"), SPREADS_TAROT["3"])
    
    drawn = []
    stats = {"Major": 0, "Wands": 0, "Cups": 0, "Swords": 0, "Pentacles": 0}
    
    for i in range(spread["count"]):
        if not deck: break
        card = deck.pop()
        is_rev = random.choice([False, False, False, True])
        if card["type"] == "Major": stats["Major"] += 1
        else: stats[card["suit"]] += 1
        
        status_text = "Xuôi" if not is_rev else "Ngược"
        drawn.append({
            "pos": spread["pos"][i],
            "name": card["name"],
            "status": status_text,
            "meaning": card["meaning"],
            "is_reversed": is_rev
        })
        
    msg = f"🔮 **KẾT QUẢ TAROT**\n👤 Querent: {user_context.get('info', 'Ẩn danh')}\n❤️ Vấn đề: {user_context.get('topic')}\n📜 Spread: {spread['name']}\n➖➖➖➖➖➖\n\n"
    for idx, item in enumerate(drawn):
        msg += f"📍 **{item['pos']}**: {item['name']} ({item['status']})\n👉 {item['meaning']}\n\n"
    
    msg += "💡 **LỜI KHUYÊN:**\n"
    if stats["Major"] >= spread["count"]/2: msg += "⚠️ Giai đoạn ĐỊNH MỆNH quan trọng, hãy cân nhắc kỹ.\n"
    else: msg += "✅ Vấn đề đời thường, có thể thay đổi bằng hành động cụ thể.\n"
    return msg

# ================= 6. LOGIC BÀI TÂY ENGINE (FULL ABSOLUTE) =================

def generate_playing_deck():
    """Tạo bộ bài 52 lá không Joker"""
    deck = []
    suits_map = {"Hearts": "♥ Cơ", "Diamonds": "♦ Rô", "Clubs": "♣ Tép", "Spades": "♠ Bích"}
    ranks_map = {"A": "Át", "2": "Hai", "3": "Ba", "4": "Bốn", "5": "Năm", "6": "Sáu", "7": "Bảy", "8": "Tám", "9": "Chín", "10": "Mười", "J": "Bồi", "Q": "Đầm", "K": "Già"}
    
    for suit_en, ranks in PLAYING_CARDS_MEANING.items():
        for rank, meaning in ranks.items():
            full_name = f"{ranks_map[rank]} {suits_map[suit_en][2:]}"
            display_name = f"{rank}{suits_map[suit_en][0]}" # VD: 10♦
            deck.append({
                "name": full_name, # Mười Rô
                "display": display_name, # 10♦
                "suit": suit_en,
                "rank": rank,
                "meaning": meaning
            })
    return deck

def execute_playing_reading(user_context):
    deck = generate_playing_deck()
    random.shuffle(deck)
    spread = SPREADS_PLAYING.get(user_context.get("spread_id", "5"), SPREADS_PLAYING["5"])
    
    drawn = []
    for i in range(spread["count"]):
        if not deck: break
        card = deck.pop()
        drawn.append(card)
        drawn[i]["pos_name"] = spread["pos"][i]
        
    # --- XÂY DỰNG NỘI DUNG TRẢ LỜI (STORYTELLING) ---
    msg = f"🎭 **KẾT QUẢ BÓI BÀI TÂY**\n"
    msg += f"👤 Người xem: {user_context.get('info', 'Ẩn danh')}\n"
    msg += f"❓ Câu hỏi: {user_context.get('question')}\n"
    msg += f"🔀 Kiểu trải: {spread['name']}\n"
    msg += "➖➖➖➖➖➖➖➖➖➖\n\n"
    
    # Danh sách bài
    msg += "🃏 **CÁC LÁ BÀI ĐƯỢC BỐC:**\n"
    for item in drawn:
        msg += f"• {item['display']} – {item['name']}\n"
    
    msg += "\n🔍 **LUẬN GIẢI CHI TIẾT:**\n"
    
    for idx, item in enumerate(drawn):
        # Xác định chất bài để dẫn dắt
        suit_intro = ""
        if item["suit"] == "Hearts": suit_intro = "Lá bài thuộc nước Cơ (Tình cảm/Gia đạo)."
        elif item["suit"] == "Diamonds": suit_intro = "Lá bài thuộc nước Rô (Tiền bạc/Vật chất)."
        elif item["suit"] == "Clubs": suit_intro = "Lá bài thuộc nước Tép (Công việc/Hành động)."
        elif item["suit"] == "Spades": suit_intro = "Lá bài thuộc nước Bích (Thử thách/Lo âu)."
        
        msg += f"🔹 **Lá {idx+1} – {item['display']} ({item['pos_name']})**\n"
        msg += f"{suit_intro} Cụ thể, **{item['name']}** mang ý nghĩa về: *{item['meaning']}*.\n"
        msg += f"Đặt vào vị trí '{item['pos_name']}', điều này cho thấy năng lượng này đang tác động trực tiếp, đòi hỏi bạn phải lưu tâm.\n\n"
        
    msg += "✅ **TỔNG KẾT TOÀN CỤC:**\n"
    # Logic tổng kết
    suits_count = {"Hearts": 0, "Diamonds": 0, "Clubs": 0, "Spades": 0}
    for item in drawn: suits_count[item["suit"]] += 1
    dom_suit = max(suits_count, key=suits_count.get)
    
    if dom_suit == "Hearts": msg += "Phần lớn các lá bài thuộc nước Cơ. Vấn đề cốt lõi lúc này bị chi phối mạnh bởi **Cảm xúc và Mối quan hệ**. Hãy lắng nghe trái tim nhưng đừng để nó lấn át lý trí.\n"
    elif dom_suit == "Diamonds": msg += "Phần lớn các lá bài thuộc nước Rô. Trọng tâm câu chuyện xoay quanh **Tài chính và Giá trị thực tế**. Đây là lúc cần tính toán kỹ lưỡng, thực dụng hơn.\n"
    elif dom_suit == "Clubs": msg += "Phần lớn các lá bài thuộc nước Tép. Đây là giai đoạn của **Hành động và Công việc**. Đừng ngồi yên suy nghĩ, hãy bắt tay vào làm ngay.\n"
    elif dom_suit == "Spades": msg += "Phần lớn các lá bài thuộc nước Bích. Cảnh báo về **Thử thách và Áp lực**. Bạn đang gặp khó khăn, nhưng đây cũng là lúc rèn luyện bản lĩnh.\n"
    
    msg += "\n💡 **LỜI KHUYÊN THỰC TẾ:**\n"
    if suits_count["Spades"] >= 2:
        msg += "Đừng vội vàng. Hiện tại có nhiều trở ngại, hãy ưu tiên sự an toàn và kiên nhẫn. "
    elif suits_count["Diamonds"] >= 2:
        msg += "Hãy quản lý tài chính chặt chẽ. Đừng đầu tư mạo hiểm lúc này. "
    else:
        msg += "Cơ hội đang mở ra. Hãy tận dụng nguồn lực hiện có và tiến bước một cách tự tin. "
        
    msg += "Thành công đến từ sự kỷ luật, không phải may mắn ngẫu nhiên."
    
    return msg

# ================= 7. QUY TRÌNH HỘI THOẠI (SESSION MANAGER) =================

def handle_session_flow(user_id, text, payload):
    session = tarot_sessions.get(user_id)
    if not session: return

    mode = session.get("mode", "TAROT") # TAROT hoặc PLAYING
    
    # ANTI-RESET
    if payload and "SPREAD_" in payload:
        spread_id = payload.replace("SPREAD_", "")
        session["spread_id"] = spread_id
        send_typing(user_id)
        
        if mode == "TAROT":
            send_text(user_id, f"🔀 Đang xào bài Tarot... Tập trung nhé...")
            res = execute_tarot_reading(session)
        else:
            send_text(user_id, f"🔀 Đang xào bài Tây... (Cắt bài 3 phần)...")
            res = execute_playing_reading(session)
            
        send_text(user_id, res)
        if user_id in tarot_sessions: del tarot_sessions[user_id]
        return

    # STEP 1: Topic -> Hỏi câu hỏi
    if session["step"] == 1:
        session["topic"] = payload if payload else text
        session["step"] = 2
        tarot_sessions[user_id] = session
        send_text(user_id, f"Bạn muốn hỏi cụ thể gì về '{session['topic']}'? (Gõ '.' để bỏ qua)")
        return

    # STEP 2: Câu hỏi -> Hỏi thông tin
    if session["step"] == 2:
        session["question"] = text
        session["step"] = 3
        tarot_sessions[user_id] = session
        send_quick_reply(user_id, "Cho mình biết Ngày sinh/Cung hoàng đạo nhé?", [("Bỏ qua", "SKIP")])
        return

    # STEP 3: Thông tin -> Chọn Spread
    if session["step"] == 3:
        session["info"] = text
        session["step"] = 4
        tarot_sessions[user_id] = session
        
        if mode == "TAROT":
            options = [("1 Lá", "SPREAD_1"), ("3 Lá", "SPREAD_3"), ("5 Lá", "SPREAD_5"), ("Celtic", "SPREAD_10")]
            send_quick_reply(user_id, "🔹 Chọn trải bài Tarot:", options)
        else:
            options = [("3 Lá (Thời gian)", "SPREAD_3"), ("5 Lá (Tổng quan)", "SPREAD_5"), ("7 Lá (Tình duyên)", "SPREAD_7")]
            send_quick_reply(user_id, "🔹 Chọn trải bài Tây:", options)
        return

# ================= 8. XỬ LÝ LỆNH CHUNG =================

def handle_command(user_id, cmd, args):
    cmd = cmd.lower()
    
    # 1. TAROT
    if cmd == "/tarot":
        tarot_sessions[user_id] = {"step": 1, "mode": "TAROT"}
        options = [("Tình yêu", "Tình yêu"), ("Công việc", "Công việc"), ("Tài chính", "Tài chính"), ("Nội tâm", "Nội tâm")]
        send_quick_reply(user_id, "🔮 **PHÒNG TAROT ONLINE**\nBạn muốn hỏi về chủ đề gì?", options)

    # 2. BÀI TÂY (MỚI)
    elif cmd == "/baitay":
        tarot_sessions[user_id] = {"step": 1, "mode": "PLAYING"}
        options = [("Tình cảm", "Tình cảm"), ("Tiền bạc", "Tiền bạc"), ("Công việc", "Công việc"), ("Vận hạn", "Vận hạn"), ("Tổng quan", "Tổng quan")]
        send_quick_reply(user_id, "🎭 **PHÒNG BÓI BÀI TÂY**\nBạn muốn xem về vấn đề gì?", options)

    # CÁC LỆNH KHÁC (GIỮ NGUYÊN)
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

    elif cmd == "/sticker":
        send_text(user_id, "🖼️ Gửi ảnh vào đây để tạo sticker.")

    elif cmd in ["/help", "menu", "hi"]:
        menu = (
            "✨➖ 🤖 **DANH SÁCH LỆNH BOT** 🤖➖✨\n"
            "                    Tronglv📸\n"
            "➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
            "     🔮 **TÂM LINH** 🔮\n"
            "✨ 1./tarot : Bói bài Tarot\n"
            "🎭 2./baitay : Bói bài Tây\n\n"
            "    🎵 **ÂM NHẠC**\n"
            "🎧 3./nhac [tên] : Tìm nhạc Youtube\n\n"
            "    🕒 **THỜI GIAN & SỰ KIỆN**\n"
            "⏰ 4./time : Xem giờ hiện tại\n"
            "⏳ 5./thptqg : Đếm ngược ngày thi\n"
            "🎉 6./hld : Ngày lễ sắp tới\n\n"
            "    📚 **TRA CỨU**\n"
            "📖 7./wiki [từ] : Tra Wikipedia\n"
            "🌐 8./gg [câu hỏi] : Link Google\n\n"
            "    🎮 **GIẢI TRÍ**\n"
            "✊ 9./kbb : Chơi Kéo Búa Bao\n"
            "🤣 10./meme : Xem ảnh chế\n"
            "🎬 11./anime : Gợi ý Anime\n\n"
            "    🎁 **GAME**\n"
            "🎟️ 12./code [game] : Giftcode game\n"
            "🆕 13./updt [game] : Thông tin phiên bản\n\n"
            "    🖼️ **HÌNH ẢNH**\n"
            "🖌️ 14./sticker : Gửi ảnh để tạo sticker\n\n"
            "*(💡 Mẹo: Nhắn số thứ tự để dùng lệnh nhanh)*"
        )
        send_text(user_id, menu)
    else:
        send_text(user_id, "Lệnh không đúng. Gõ /help để xem Menu.")

# ================= 9. MAIN HANDLER =================

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
                        handle_session_flow(sender_id, text, payload)
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
                        else: send_text(sender_id, "Gõ /help hoặc số 1-14.")

        return "ok", 200
    except: return "ok", 200

if __name__ == "__main__":
    app.run(port=5000)
