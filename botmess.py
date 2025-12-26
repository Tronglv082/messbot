import os
from flask import Flask, request
import requests
from datetime import datetime
import google.generativeai as genai
import wikipedia
import random

app = Flask(__name__)

# --- CẤU HÌNH ---
# PAGE_ACCESS_TOKEN: Token của bạn
PAGE_ACCESS_TOKEN = "EAAJpiB62hRwBQYOZBwZCNSFTIgGlnhMCNtZAfsTuHsnFXIcOcg68xQWXfrF9tJ73L9gRaleeXwMRql4SmPPJzStmSZBzvjdrVGeatHqEi2Gw4JnDoZCqmtg1iXcVMIVykP197nZCHbINBvkaxz0fn8sPmMhPDOJgKMZBGLSnMl6Ak5C6SecqkRtcFiYfrkJgMt2RCeJpDaR3QZDZD"
# VERIFY_TOKEN: bot 123 (Có dấu cách)
VERIFY_TOKEN = "bot 123"
# GEMINI API KEY: Key MỚI của bạn
GEMINI_API_KEY = "AIzaSyCLu6ZfQocgW3FthZDNKz2Vb0hQ90w8b6A"

# Cấu hình AI (Dùng bản Flash cho nhanh và miễn phí)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Cấu hình Wikipedia tiếng Việt
wikipedia.set_lang("vi")

# --- HÀM GỬI TIN NHẮN ---
def send_message(recipient_id, text):
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    
    # Cắt tin nhắn nếu quá dài (Facebook giới hạn 2000 ký tự)
    if len(text) > 1900:
        text = text[:1900] + "... (còn nữa)"
        
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    try:
        r = requests.post("https://graph.facebook.com/v19.0/me/messages", params=params, headers=headers, json=data)
        if r.status_code != 200:
            print(f"❌ Lỗi gửi FB: {r.text}")
    except Exception as e:
        print(f"❌ Lỗi mạng: {e}")

# --- HÀM HỎI GEMINI ---
def ask_gemini(prompt):
    try:
        # Thêm chỉ dẫn để bot trả lời ngắn gọn, vui vẻ hơn
        system_instruction = "Bạn là một trợ lý ảo vui tính. Hãy trả lời ngắn gọn, súc tích."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Lỗi Gemini: {e}")
        return "Server AI đang quá tải, thử lại sau 1 lát nhé!"

# --- XỬ LÝ LỆNH ---
def process_command(message_text, sender_id):
    msg = message_text.strip()
    msg_lower = msg.lower()

    # 1. Menu Hướng dẫn
    if msg_lower == "/help" or msg_lower == "menu":
        return (
            "🤖 MENU BOT 🤖\n"
            "------------------\n"
            "1. /wiki [từ khóa]: Tra cứu Wiki\n"
            "2. /thptqg: Đếm ngược ngày thi\n"
            "3. /nhac: Gợi ý nhạc hay\n"
            "4. Chat tự do: Bot sẽ tự trả lời\n"
        )

    # 2. Đếm ngược thi THPTQG
    elif msg_lower == "/thptqg":
        days = (datetime(2026, 6, 12) - datetime.now()).days
        return f"⏳ Còn {days} ngày nữa là đến 12/6/2026. Cố lên các sĩ tử!"

    # 3. Tra cứu Wikipedia
    elif msg_lower.startswith("/wiki"):
        keyword = msg[5:].strip()
        if not keyword: return "Nhập từ khóa đi bạn ơi. VD: /wiki Hà Nội"
        try:
            summary = wikipedia.summary(keyword, sentences=2)
            return f"📚 Wiki: {summary}"
        except:
            return "Không tìm thấy thông tin trên Wiki."

    # 4. Gợi ý nhạc
    elif msg_lower == "/nhac":
        songs = ["Em của ngày hôm qua", "Chúng ta của tương lai", "Cắt đôi nỗi sầu", "Nấu ăn cho em", "Thiên Lý Ơi"]
        return f"🎵 Nghe bài này đi: {random.choice(songs)}"

    # 5. CHAT TỰ ĐỘNG (Dùng AI Key Mới)
    else:
        # Gửi tin nhắn chờ để user đỡ sốt ruột
        send_message(sender_id, "💬 Đang nhập...") 
        return ask_gemini(msg)

# --- WEBHOOK ---
@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    # Xác minh Token (Facebook gọi đến)
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Sai Token", 403

    # Nhận tin nhắn từ người dùng
    if request.method == 'POST':
        try:
            data = request.get_json()
            if data and data.get("object") == "page":
                for entry in data["entry"]:
                    for event in entry.get("messaging", []):
                        if event.get("message") and "text" in event["message"]:
                            sender_id = event["sender"]["id"]
                            text = event["message"]["text"]
                            
                            # Xử lý
                            response = process_command(text, sender_id)
                            send_message(sender_id, response)
            return "OK", 200
        except Exception as e:
            print(f"Lỗi Webhook: {e}")
            return "Error", 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
