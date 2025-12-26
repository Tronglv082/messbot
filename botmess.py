import os
import requests
import datetime
import wikipedia
import google.generativeai as genai
from flask import Flask, request
from youtube_search import YoutubeSearch
import random

app = Flask(__name__)

# ================= CẤU HÌNH BOT (THAY ĐỔI TẠI ĐÂY) =================
# 1. Page Access Token (Lấy từ Facebook Developers)
PAGE_ACCESS_TOKEN = "THAY_ACCESS_TOKEN_CUA_BAN_VAO_DAY"
# 2. Verify Token (Bạn tự đặt, ví dụ: bot123)
VERIFY_TOKEN = "bot123"
# 3. Gemini API Key (Lấy từ Google AI Studio)
GEMINI_API_KEY = "THAY_GEMINI_API_KEY_CUA_BAN_VAO_DAY"
# ===================================================================

# Cấu hình Gemini & Wikipedia
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash') # Dùng bản Flash cho nhanh
    wikipedia.set_lang('vi') # Thiết lập tiếng Việt cho Wiki
except Exception as e:
    print(f"Lỗi cấu hình API: {e}")

# --- CÁC HÀM CHỨC NĂNG ---

def send_message(recipient_id, text):
    """Gửi tin nhắn văn bản về Messenger"""
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    try:
        r = requests.post("https://graph.facebook.com/v19.0/me/messages", params=params, headers=headers, json=data)
        if r.status_code != 200:
            print(f"❌ Lỗi gửi tin: {r.text}")
    except Exception as e:
        print(f"❌ Lỗi mạng: {e}")

def get_gemini_response(prompt):
    """Hỏi Gemini AI"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini đang bận hoặc lỗi key: {str(e)}"

def search_youtube(keyword):
    """Tìm nhạc trên YouTube"""
    try:
        # Tìm 1 kết quả đầu tiên
        results = YoutubeSearch(keyword, max_results=1).to_dict()
        if results:
            video = results[0]
            title = video['title']
            link = f"https://www.youtube.com{video['url_suffix']}"
            return f"🎵 Tìm thấy: {title}\n🔗 Link: {link}"
        else:
            return "❌ Không tìm thấy bài hát nào."
    except Exception as e:
        return f"❌ Lỗi tìm nhạc: {e}"

def get_wiki_summary(keyword):
    """Tra cứu Wikipedia"""
    try:
        # Tìm kiếm và lấy tóm tắt 3 câu đầu
        summary = wikipedia.summary(keyword, sentences=3)
        return f"📚 Wikipedia: {keyword}\n\n{summary}\n\n(Nguồn: Wikipedia Tiếng Việt)"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"⚠️ Từ khóa này có nhiều nghĩa: {', '.join(e.options[:5])}..."
    except wikipedia.exceptions.PageError:
        return "❌ Không tìm thấy thông tin trên Wikipedia."
    except Exception as e:
        return "⚠️ Lỗi tra cứu Wikipedia."

def get_thptqg_countdown():
    """Đếm ngược thi THPTQG 2026"""
    target_date = datetime.datetime(2026, 6, 12, 7, 0, 0) # 7h sáng 12/6
    now = datetime.datetime.now()
    remaining = target_date - now
    
    if remaining.total_seconds() <= 0:
        return "🎉 Đã qua kỳ thi THPTQG 2026 rồi!"
    
    days = remaining.days
    hours, remainder = divmod(remaining.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"⏳ ĐẾM NGƯỢC THPTQG 2026 (12/6/2026):\n👉 Còn: {days} ngày, {hours} giờ, {minutes} phút, {seconds} giây.\n💪 Cố lên sĩ tử!"

# --- XỬ LÝ LOGIC CHÍNH ---

def process_command(message, sender_id):
    msg = message.strip()
    msg_lower = msg.lower()

    # 1. /help
    if msg_lower == "/help":
        return (
            "🤖 MENU BOT:\n"
            "------------------\n"
            "1. /nhac <tên bài>: Tìm nhạc\n"
            "2. /nhac: Nghe bài ngẫu nhiên\n"
            "3. /wiki <từ khóa>: Tra cứu Wiki\n"
            "4. /gemini <câu hỏi>: Hỏi AI\n"
            "5. /time: Xem giờ\n"
            "6. /thptqg: Đếm ngược thi 2026"
        )

    # 2. /time
    elif msg_lower == "/time":
        now = datetime.datetime.now()
        return f"🕒 Bây giờ là: {now.strftime('%H:%M:%S')} - Ngày {now.strftime('%d/%m/%Y')}"

    # 3. /thptqg
    elif msg_lower == "/thptqg":
        return get_thptqg_countdown()

    # 4. /nhac (Tìm cụ thể hoặc Ngẫu nhiên)
    elif msg_lower.startswith("/nhac"):
        query = msg[5:].strip()
        if not query:
            # Nếu không nhập tên, random một bài nhạc trending
            list_random = ["Sơn Tùng MTP", "Nhạc Lofi Chill", "Nhạc trẻ Remix", "Ed Sheeran"]
            query = random.choice(list_random)
            send_message(sender_id, f"🔍 Đang chọn nhạc ngẫu nhiên chủ đề '{query}'...")
        else:
             send_message(sender_id, f"🔍 Đang tìm bài '{query}' trên YouTube...")
        
        return search_youtube(query)

    # 5. /wiki
    elif msg_lower.startswith("/wiki"):
        query = msg[5:].strip()
        if not query: return "⚠️ Vui lòng nhập từ khóa. Ví dụ: /wiki Hồ Chí Minh"
        send_message(sender_id, "📖 Đang tra từ điển bách khoa...")
        return get_wiki_summary(query)

    # 6. /gemini
    elif msg_lower.startswith("/gemini"):
        query = msg[7:].strip()
        if not query: return "⚠️ Vui lòng nhập câu hỏi."
        send_message(sender_id, "🤖 Gemini đang suy nghĩ...")
        return get_gemini_response(query)

    # Mặc định: Nếu không phải lệnh, có thể cho Gemini trả lời luôn hoặc hướng dẫn
    else:
        return 'Bot không hiểu. Gõ "/help" để xem hướng dẫn.'

# --- SERVER WEBHOOK ---

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    # Xác thực Verify Token (Facebook gọi GET)
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Sai Token", 403

    # Nhận tin nhắn (Facebook gọi POST)
    if request.method == 'POST':
        try:
            data = request.get_json()
            if data and data.get("object") == "page":
                for entry in data["entry"]:
                    for event in entry.get("messaging", []):
                        if event.get("message") and "text" in event["message"]:
                            sender_id = event["sender"]["id"]
                            text = event["message"]["text"]
                            
                            # Xử lý lệnh
                            response_text = process_command(text, sender_id)
                            send_message(sender_id, response_text)
            return "OK", 200
        except Exception as e:
            print(f"Lỗi Webhook: {e}")
            return "Lỗi", 500

if __name__ == "__main__":
    # Chạy trên cổng 5000
    app.run(port=5000, debug=True)
