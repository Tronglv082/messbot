import os
import sys
import json
import random
import datetime
import pytz
import requests
import wikipedia
from flask import Flask, request

# ================= CẤU HÌNH BOT =================
app = Flask(__name__)

ACCESS_TOKEN = "EAAJpiB62hRwBQQjVYulX1G6CRANSKLCZBPxF4UhFSZCCebg7uSGCcZAPOti7jjXgUNZCOOfe624MIZBfuCAZCNfaZANLCcKxO3QSomx8mW4xhbOlGzsXwrKDiuO5avRfDnP4DNQdrZB26ni8IZCfqdzjczrbITe2snoFBZBJDUNxxUZC922FvjuIZArIwLN6nqjvwb7HxWNGxIkWawZDZD"
VERIFY_TOKEN = "bot 123"

# ================= DỮ LIỆU & CẤU HÌNH TAROT =================

# 1. Định nghĩa Bộ bài 78 lá
MAJORS = {
    0: ("The Fool", "Khởi đầu mới, tự do", "Liều lĩnh, khờ khạo"),
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
SUITS = {"Wands": "Lửa - Hành động", "Cups": "Nước - Cảm xúc", "Swords": "Khí - Trí tuệ", "Pentacles": "Đất - Tiền bạc"}
RANKS = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"]

# 2. Định nghĩa các kiểu trải bài (Spreads)
SPREADS = {
    "1": {"name": "One Card (Thông điệp ngày)", "count": 1, "pos": ["Lời khuyên chính"]},
    "3": {"name": "Three Card (Quá khứ - HT - TL)", "count": 3, "pos": ["Quá khứ / Nguyên nhân", "Hiện tại / Tình huống", "Tương lai / Kết quả"]},
    "5": {"name": "Five Card Cross (Giải quyết vấn đề)", "count": 5, "pos": ["Vấn đề hiện tại", "Thách thức", "Gốc rễ", "Lời khuyên", "Kết quả"]},
    "7": {"name": "Horseshoe (Móng ngựa)", "count": 7, "pos": ["Quá khứ", "Hiện tại", "Tương lai gần", "Thái độ", "Môi trường", "Hy vọng", "Kết quả"]},
    "10": {"name": "Celtic Cross (Chi tiết)", "count": 10, "pos": ["Hiện tại", "Cản trở", "Tiềm thức", "Quá khứ", "Ý thức", "Tương lai gần", "Bản thân", "Môi trường", "Hy vọng/Sợ hãi", "Kết quả cuối cùng"]},
    "12": {"name": "Zodiac (12 Cung - Tổng quan năm)", "count": 12, "pos": [f"Nhà {i+1}" for i in range(12)]}
}

# ================= QUẢN LÝ TRẠNG THÁI (SESSION) =================
# Lưu trạng thái người dùng đang ở bước nào của quy trình Tarot
# Structure: {user_id: {"step": 1, "topic": "love", "question": "...", ...}}
tarot_sessions = {}
kbb_state = {} # Game Kéo búa bao

# ================= HÀM HỖ TRỢ GỬI TIN =================

def send_typing(user_id, duration=1):
    """Giả lập đang soạn tin"""
    headers = {"Content-Type": "application/json"}
    requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers=headers, data=json.dumps({"recipient": {"id": user_id}, "sender_action": "typing_on"}))

def send_text(user_id, text):
    headers = {"Content-Type": "application/json"}
    requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers=headers, data=json.dumps({"recipient": {"id": user_id}, "message": {"text": text}}))

def send_quick_reply(user_id, text, options):
    q_replies = [{"content_type": "text", "title": t, "payload": p} for t, p in options]
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"recipient": {"id": user_id}, "messaging_type": "RESPONSE", "message": {"text": text, "quick_replies": q_replies}})
    requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers=headers, data=data)

# ================= LOGIC TAROT ENGINE (XỬ LÝ LÕI) =================

def generate_full_deck():
    deck = []
    # Major Arcana
    for i, (name, up, rev) in MAJORS.items():
        deck.append({"name": f"{name} (Ẩn Chính)", "up": up, "rev": rev, "type": "Major"})
    # Minor Arcana
    for s_name, s_desc in SUITS.items():
        for rank in RANKS:
            name = f"{rank} of {s_name}"
            deck.append({"name": name, "up": f"{rank} trong {s_desc}", "rev": f"Tắc nghẽn/Ngược lại của {rank}", "type": "Minor"})
    return deck

def perform_tarot_reading(user_context):
    """Giai đoạn 3 & 4: Xào bài và Giải bài"""
    deck = generate_full_deck()
    random.shuffle(deck) # Xào bài
    
    spread_id = user_context.get("spread_id", "3")
    spread_info = SPREADS[spread_id]
    count = spread_info["count"]
    
    # Bốc bài
    drawn_cards = []
    for i in range(count):
        card = deck.pop()
        is_reversed = random.choice([True, False, False]) # 33% cơ hội bài ngược
        drawn_cards.append({
            "position": spread_info["pos"][i],
            "card": card,
            "is_reversed": is_reversed
        })
    
    # Tạo Output JSON (Internal Use)
    result_json = {
        "user_context": user_context,
        "spread_type": spread_info["name"],
        "cards": drawn_cards,
        "overall_message": "Dựa trên các lá bài, năng lượng của bạn đang chuyển biến..."
    }
    return result_json

def format_tarot_result(result_json):
    """Chuyển JSON thành văn bản tự nhiên cho Messenger"""
    ctx = result_json["user_context"]
    cards = result_json["cards"]
    
    msg = f"🔮 **KẾT QUẢ TRẢI BÀI** 🔮\n"
    msg += f"👤 Người hỏi: {ctx.get('info', 'Ẩn danh')}\n"
    msg += f"❤️ Vấn đề: {ctx.get('topic')} | 📝 Spread: {result_json['spread_type']}\n"
    msg += "➖➖➖➖➖➖➖➖\n\n"
    
    major_count = 0
    for item in cards:
        c = item["card"]
        pos = item["position"]
        status = "🔻 NGƯỢC" if item["is_reversed"] else "🔺 XUÔI"
        meaning = c["rev"] if item["is_reversed"] else c["up"]
        
        if c["type"] == "Major": major_count += 1
        
        msg += f"📍 **{pos}:** {c['name']} ({status})\n"
        msg += f"👉 *{meaning}*\n\n"
    
    msg += "➖➖➖➖➖➖➖➖\n"
    msg += "💡 **LỜI KHUYÊN TỔNG HỢP:**\n"
    if major_count >= len(cards)/2:
        msg += "⚠️ Bạn đang trải qua giai đoạn mang tính ĐỊNH MỆNH (nhiều lá Ẩn Chính). Hãy cân nhắc kỹ mọi quyết định lớn.\n"
    else:
        msg += "✅ Vấn đề này mang tính đời thường, bạn hoàn toàn có thể kiểm soát bằng hành động cụ thể.\n"
        
    msg += "\n(Hãy hít thở sâu và đón nhận thông điệp một cách cởi mở nhé ✨)"
    return msg

# ================= QUY TRÌNH HỘI THOẠI TAROT (4 GIAI ĐOẠN) =================

def handle_tarot_process(user_id, text):
    """State Machine điều khiển quy trình Tarot"""
    session = tarot_sessions.get(user_id)
    step = session["step"]
    
    # --- GIAI ĐOẠN 1: THU THẬP THÔNG TIN ---
    
    if step == 1: # Nhận Topic -> Hỏi câu hỏi cụ thể
        session["topic"] = text
        session["step"] = 2
        send_text(user_id, f"Tuyệt vời. Bạn muốn hỏi cụ thể điều gì về '{text}'?\n(Ví dụ: 'Sắp tới mình có người yêu không?' hoặc 'Tài chính tháng sau thế nào?')")
        return

    if step == 2: # Nhận Câu hỏi -> Hỏi thông tin cá nhân (Optional)
        session["question"] = text
        session["step"] = 3
        send_text(user_id, "Để kết nối năng lượng tốt hơn, bạn có thể cho mình biết Ngày sinh & Cung hoàng đạo không?\n(Gõ 'Bỏ qua' nếu muốn giữ bí mật nhé 😉)")
        return

    if step == 3: # Nhận Info -> Chuyển sang Giai đoạn 2 (Chọn Spread)
        session["info"] = text if text.lower() != "bỏ qua" else "Ẩn danh"
        session["step"] = 4
        
        # Gợi ý Spread dựa trên Topic (Logic đơn giản hóa)
        options = [
            ("1 Lá (Nhanh)", "SPREAD_1"),
            ("3 Lá (Cơ bản)", "SPREAD_3"),
            ("5 Lá (Chi tiết)", "SPREAD_5"),
            ("Celtic (10 lá)", "SPREAD_10")
        ]
        send_quick_reply(user_id, "🔹 GIAI ĐOẠN 2: CHỌN TRẢI BÀI\nBạn muốn mình trải bài theo cách nào?", options)
        return

    # --- GIAI ĐOẠN 2 & 3: CHỌN SPREAD & XÀO BÀI ---

    if step == 4: # Nhận Spread -> Xào bài -> Giải bài
        if "SPREAD_" in text: # Nếu bấm nút
            spread_id = text.replace("SPREAD_", "")
        elif text in ["1", "3", "5", "7", "10", "12"]: # Nếu gõ số
            spread_id = text
        else:
            spread_id = "3" # Mặc định
            
        session["spread_id"] = spread_id
        
        # Mô phỏng Giai đoạn 3: Xào bài
        send_text(user_id, f"Được rồi, mình sẽ dùng trải bài {SPREADS[spread_id]['name']}.")
        send_typing(user_id)
        send_text(user_id, "🔀 Đang xào bài... Hít thở sâu và tập trung vào câu hỏi nhé...")
        
        # --- GIAI ĐOẠN 4: GIẢI BÀI & OUTPUT ---
        import time
        # time.sleep(2) # (Trên server thật thì sleep, ở đây bỏ qua để phản hồi nhanh)
        
        result_json = perform_tarot_reading(session)
        final_msg = format_tarot_result(result_json)
        
        send_text(user_id, final_msg)
        
        # Kết thúc session
        del tarot_sessions[user_id]
        return

# ================= XỬ LÝ LỆNH CHUNG =================

def handle_command(user_id, command, args):
    if command == "/tarot":
        # BẮT ĐẦU GIAI ĐOẠN 1: KHỞI TẠO SESSION
        tarot_sessions[user_id] = {"step": 1}
        options = [
            ("❤️ Tình yêu", "Tình yêu"),
            ("💼 Công việc", "Công việc"),
            ("💰 Tài chính", "Tài chính"),
            ("🧘 Nội tâm", "Nội tâm")
        ]
        send_quick_reply(user_id, "🔮 Chào mừng đến với phòng Tarot.\n🔹 GIAI ĐOẠN 1: THU THẬP THÔNG TIN\nBạn muốn hỏi về vấn đề gì?", options)
        return

    # Các lệnh cũ vẫn giữ nguyên
    elif command == "/help":
        send_text(user_id, "🤖 MENU: /tarot (Bói chuẩn 4 bước), /time, /wiki, /gg, /kbb, /nhac")
    elif command == "/gg":
        q = " ".join(args).replace(" ", "+")
        send_text(user_id, f"👉 Link Google: https://www.google.com/search?q={q}")
    elif command == "/kbb":
        kbb_state[user_id] = "WAITING"
        send_quick_reply(user_id, "Kéo Búa Bao?", [("✌️", "KEO"), ("✊", "BUA"), ("✋", "BAO")])
    elif command == "/time":
        now = datetime.datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
        send_text(user_id, f"🕒 {now.strftime('%H:%M:%S - %d/%m/%Y')}")
    else:
        send_text(user_id, "Lệnh không đúng. Gõ /help hoặc thử /tarot xem sao!")

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

                # 1. Xử lý Quick Reply (Payload)
                payload = None
                if "message" in event and "quick_reply" in event["message"]:
                    payload = event["message"]["quick_reply"]["payload"]
                
                # 2. Xử lý Text
                text = None
                if "message" in event and "text" in event["message"]:
                    text = event["message"]["text"].strip()

                # ƯU TIÊN 1: Xử lý Tarot Session (Nếu đang trong quy trình)
                if sender_id in tarot_sessions:
                    # Nếu có payload từ nút bấm thì dùng payload, không thì dùng text
                    content = payload if payload else text
                    handle_tarot_process(sender_id, content)
                    continue

                # ƯU TIÊN 2: Xử lý Game KBB
                if sender_id in kbb_state and payload:
                    bot = random.choice(["KEO", "BUA", "BAO"])
                    res = "Hòa" if payload==bot else ("Thắng" if (payload=="KEO" and bot=="BAO") or (payload=="BUA" and bot=="KEO") or (payload=="BAO" and bot=="BUA") else "Thua")
                    send_text(sender_id, f"Bot: {bot} | Bạn: {payload} => {res}")
                    del kbb_state[sender_id]
                    continue

                # ƯU TIÊN 3: Lệnh thường
                if text and text.startswith("/"):
                    parts = text.split()
                    handle_command(sender_id, parts[0], parts[1:])
                elif text:
                    send_text(sender_id, "Gõ /tarot để xem bói hoặc /help để xem menu.")

        return "ok", 200
    return "ok", 404

if __name__ == "__main__":
    app.run(port=5000)
