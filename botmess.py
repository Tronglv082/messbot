import os
from flask import Flask, request
import requests
from datetime import datetime
import google.generativeai as genai

app = Flask(__name__)

# --- CẤU HÌNH (KEYS CỦA BẠN) ---
PAGE_ACCESS_TOKEN = "EAAJpiB62hRwBQYOZBwZCNSFTIgGlnhMCNtZAfsTuHsnFXIcOcg68xQWXfrF9tJ73L9gRaleeXwMRql4SmPPJzStmSZBzvjdrVGeatHqEi2Gw4JnDoZCqmtg1iXcVMIVykP197nZCHbINBvkaxz0fn8sPmMhPDOJgKMZBGLSnMl6Ak5C6SecqkRtcFiYfrkJgMt2RCeJpDaR3QZDZD"
VERIFY_TOKEN = "bot 123"
GEMINI_API_KEY = "AIzaSyCG0bMJtdlitBC_AVRyMC2JV8aSp3N9GM8"

# Cấu hình Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- HÀM GỬI TIN NHẮN FACEBOOK ---
def send_message(recipient_id, text):
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    r = requests.post("https://graph.facebook.com/v19.0/me/messages", params=params, headers=headers, json=data)
    if r.status_code != 200:
        print(f"Lỗi gửi: {r.status_code}, {r.text}")

# --- HÀM HỎI GEMINI ---
def get_gemini_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Gemini đang bận, vui lòng thử lại sau."

# --- XỬ LÝ LỆNH ---
def process_command(message_text, sender_id):
    msg = message_text.strip()
    msg_lower = msg.lower()

    # 1. /time
    if msg_lower == "/time":
        now = datetime.now()
        return f"🕒 Bây giờ là: {now.strftime('%H:%M:%S')} ngày {now.strftime('%d/%m/%Y')}"

    # 2. Hi
    elif msg_lower == "hi":
        return 'Xin chào, mik là bot tự động vui lòng gõ "/help" để được hỗ trợ'

    # 3. /help
    elif msg_lower == "/help":
        return (
            "📌 DANH SÁCH LỆNH:\n"
            "------------------\n"
            "1. /time: Xem giờ hiện tại\n"
            "2. /thptqg: Đếm ngược thi THPTQG 2026\n"
            "3. /gemini [câu hỏi]: Hỏi AI (VD: /gemini Tóm tắt lịch sử)\n"
            "4. /help: Xem hướng dẫn"
        )

    # 4. /thptqg
    elif msg_lower == "/thptqg":
        target_date = datetime(2026, 6, 12)
        today = datetime.now()
        remaining = target_date - today
        if remaining.days > 0:
            return f"⏳ Còn {remaining.days} ngày nữa là đến 12/6/2026."
        else:
            return "Đã qua ngày thi rồi!"

    # 5. /gemini
    elif msg_lower.startswith("/gemini"):
        question = msg[7:].strip()
        if not question:
            return "Vui lòng nhập câu hỏi sau lệnh. Ví dụ: /gemini Viết đoạn văn về mùa thu"
        send_message(sender_id, "🤖 Đang suy nghĩ...") # Phản hồi nhanh để user biết
        return get_gemini_response(question)

    # Mặc định
    else:
        return 'Bot không hiểu. Gõ "/help" để xem lệnh.'

# --- WEBHOOK (QUAN TRỌNG: Đã thêm /webhook) ---
@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    # 1. Xác minh Verify Token
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Sai Verify Token", 403

    # 2. Nhận tin nhắn
    if request.method == 'POST':
        data = request.get_json()
        if data.get("object") == "page":
            for entry in data["entry"]:
                for event in entry.get("messaging", []):
                    if event.get("message") and "text" in event["message"]:
                        sender_id = event["sender"]["id"]
                        message_text = event["message"]["text"]
                        
                        # Xử lý và trả lời
                        response = process_command(message_text, sender_id)
                        send_message(sender_id, response)
        return "OK", 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)