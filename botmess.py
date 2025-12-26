import os
import requests
import datetime
import wikipedia
import google.generativeai as genai
from flask import Flask, request
from youtube_search import YoutubeSearch
import random

app = Flask(__name__)

# ================= CẤU HÌNH BOT (ĐÃ ĐIỀN SẴN) =================
# 1. Page Access Token (Token EAAJ... của bạn)
PAGE_ACCESS_TOKEN = "EAAJpiB62hRwBQYOZBwZCNSFTIgGlnhMCNtZAfsTuHsnFXIcOcg68xQWXfrF9tJ73L9gRaleeXwMRql4SmPPJzStmSZBzvjdrVGeatHqEi2Gw4JnDoZCqmtg1iXcVMIVykP197nZCHbINBvkaxz0fn8sPmMhPDOJgKMZBGLSnMl6Ak5C6SecqkRtcFiYfrkJgMt2RCeJpDaR3QZDZD"

# 2. Verify Token (Token kiểm duyệt bạn đặt)
VERIFY_TOKEN = "bot 123"

# 3. Gemini API Key (Key AIza... của bạn)
GEMINI_API_KEY = "AIzaSyCG0bMJtdlitBC_AVRyMC2JV8aSp3N9GM8"

# ================= KHỞI TẠO DỊCH VỤ =================
# Cấu hình Gemini AI
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # Dùng bản Flash cho phản hồi nhanh
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"❌ Lỗi cấu hình Gemini: {e}")

# Cấu hình Wikipedia Tiếng Việt
wikipedia.set_lang('vi')

# --- CÁC HÀM XỬ LÝ CHỨC NĂNG ---

def send_message(recipient_id, text):
    """Gửi tin nhắn trả lời về Messenger"""
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    try:
        r = requests.post("https://graph.facebook.com/v19.0/me/messages", params=params, headers=headers, json=data)
        if r.status_code != 200:
            print(f"❌ Lỗi gửi tin nhắn: {r.text}")
    except Exception as e:
        print(f"❌ Lỗi mạng: {e}")

def get_gemini_response(prompt):
    """Hỏi Gemini AI"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini đang gặp lỗi: {str(e)}"

def search_youtube(keyword):
    """Tìm kiếm video/nhạc trên YouTube"""
    try:
        # Tìm 1 kết quả đầu tiên
        results = YoutubeSearch(keyword, max_results=1).to_dict()
        if results:
            video = results[0]
            title = video.get('title', 'Không có tiêu đề')
            # Tạo link xem
            link = f"https://www.youtube.com/watch?v={video['id']}"
            return f"🎵 Đã tìm thấy bài hát:\n📌 Tên: {title}\n🔗 Link: {link}\n(Bạn nhấn vào link để nghe nhé!)"
        else:
            return f"❌ Không tìm thấy bài hát nào cho từ khóa: '{keyword}'"
    except Exception as e:
        return f"❌ Lỗi khi tìm nhạc: {str(e)}"

def get_wiki_summary(keyword):
    """Tra cứu Wikipedia"""
    try:
        # Lấy tóm tắt 3 câu đầu
        summary = wikipedia.summary(keyword, sentences=3)
        return f"📚 Wikipedia: {keyword}\n\n{summary}\n\n(Nguồn: Wikipedia Tiếng Việt)"
    except wikipedia.exceptions.DisambiguationError as e:
        # Nếu từ khóa có nhiều nghĩa
        options = ', '.join(e.options[:3])
        return f"⚠️ Từ khóa này có nhiều nghĩa. Ý bạn là: {options}?"
    except wikipedia.exceptions.PageError:
        return "❌ Không tìm thấy thông tin này trên Wikipedia."
    except Exception:
        return "⚠️ Có lỗi khi tra cứu thông tin."

def get_thptqg_countdown():
    """Đếm ngược ngày thi 12/6/2026"""
    target_date = datetime.datetime(2026, 6, 12, 0, 0, 0)
    now = datetime.datetime.now()
    remaining = target_date - now
    
    if remaining.total_seconds() <= 0:
        return "🎉 Đã qua ngày 12/6/2026 rồi!"
    
    days = remaining.days
    hours, remainder = divmod(remaining.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return (f"⏳ ĐẾM NGƯỢC THPTQG 2026 (12/06/2026):\n"
            f"👉 Còn: {days} ngày, {hours} giờ, {minutes} phút, {seconds} giây.\n"
            f"🔥 Học bài đi đừng lướt Facebook nữa!")

# --- XỬ LÝ LỆNH TỪ NGƯỜI DÙNG ---

def process_command(message, sender_id):
    msg = message.strip()
    msg_lower = msg.lower()

    # 1. /help
    if msg_lower == "/help":
        return (
            "🤖 DANH SÁCH LỆNH:\n"
            "------------------\n"
            "1. /nhac [tên bài]: Tìm và gửi link nhạc\n"
            "2. /nhac: Gợi ý nhạc ngẫu nhiên\n"
            "3. /time: Xem ngày giờ hiện tại\n"
            "4. /thptqg: Đếm ngược thi 2026\n"
            "5. /wiki [từ khóa]: Tra cứu kiến thức\n"
            "6. /gemini [câu hỏi]: Chat với AI\n"
            "7. /help: Xem menu này"
        )

    # 2. /time
    elif msg_lower == "/time":
        now = datetime.datetime.now()
        return f"🕒 Bây giờ là: {now.strftime('%H:%M:%S')} - Ngày {now.strftime('%d/%m/%Y')}"

    # 3. /thptqg
    elif msg_lower == "/thptqg":
        return get_thptqg_countdown()

    # 4. /nhac
    elif msg_lower.startswith("/nhac"):
        query = msg[5:].strip() # Lấy phần sau chữ /nhac
        if not query:
            # Nếu không nhập tên, random một từ khóa
            random_keys = ["Nhạc Lofi Chill", "Sơn Tùng MTP", "Nhạc trẻ Remix", "US-UK Billboard"]
            query = random.choice(random_keys)
            send_message(sender_id, f"🎲 Bạn không nhập tên, bot sẽ chọn ngẫu nhiên: {query}")
        else:
             send_message(sender_id, f"🔎 Đang tìm bài '{query}' trên YouTube...")
        
        return search_youtube(query)

    # 5. /wiki
    elif msg_lower.startswith("/wiki"):
        query = msg[5:].strip()
        if not query:
            return "⚠️ Bạn chưa nhập từ khóa. Ví dụ: /wiki Hà Nội"
        send_message(sender_id, "📖 Đang tra cứu bách khoa toàn thư...")
        return get_wiki_summary(query)

    # 6. /gemini
    elif msg_lower.startswith("/gemini"):
        query = msg[7:].strip()
        if not query:
            return "⚠️ Bạn chưa nhập câu hỏi. Ví dụ: /gemini Viết một bài thơ"
        send_message(sender_id, "🤖 Gemini đang suy nghĩ...")
        return get_gemini_response(query)

    # Mặc định (Không phải lệnh)
    else:
        # Có thể chọn: Bot im lặng, hoặc hướng dẫn dùng /help
        return 'Bot không hiểu lệnh này. Gõ "/help" để xem danh sách lệnh nhé!'

# --- CẤU HÌNH WEBHOOK FLASK ---

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    # 1. Xác minh Verify Token (Khi bạn nhấn Verify trên Facebook)
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Sai Verify Token", 403

    # 2. Nhận tin nhắn từ người dùng
    if request.method == 'POST':
        try:
            data = request.get_json()
            if data and data.get("object") == "page":
                for entry in data["entry"]:
                    for event in entry.get("messaging", []):
                        if event.get("message") and "text" in event["message"]:
                            sender_id = event["sender"]["id"]
                            message_text = event["message"]["text"]
                            
                            # Xử lý logic và lấy câu trả lời
                            response_text = process_command(message_text, sender_id)
                            
                            # Gửi phản hồi
                            send_message(sender_id, response_text)
            return "OK", 200
        except Exception as e:
            print(f"Lỗi Webhook: {e}")
            return "Error", 500

if __name__ == "__main__":
    # Chạy server ở cổng 5000
    app.run(port=5000, debug=True)
