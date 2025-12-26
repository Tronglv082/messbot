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

# ================= CẤU HÌNH BOT =================
app = Flask(__name__)

# Token bạn đã cung cấp
ACCESS_TOKEN = "EAAJpiB62hRwBQYOZBwZCNSFTIgGlnhMCNtZAfsTuHsnFXIcOcg68xQWXfrF9tJ73L9gRaleeXwMRql4SmPPJzStmSZBzvjdrVGeatHqEi2Gw4JnDoZCqmtg1iXcVMIVykP197nZCHbINBvkaxz0fn8sPmMhPDOJgKMZBGLSnMl6Ak5C6SecqkRtcFiYfrkJgMt2RCeJpDaR3QZDZD"
VERIFY_TOKEN = "bot 123"

# Cấu hình ngôn ngữ cho Wikipedia
wikipedia.set_lang("vi")

# Biến toàn cục để lưu trạng thái game Kéo Búa Bao
kbb_state = {} 

# Dữ liệu giả lập cho Game Code và Tarot (Vì không có API chính thức free ổn định)
GAME_CODES = {
    "genshin": ["GENSHINGIFT", "CA3BLTURGH9D", "RTJUNRSHTREW"],
    "hsr": ["STARRAILGIFT", "HSRVER10JRL", "MB6N2TVCSQ9F"],
    "wuwa": ["WUWA2024", "WUTHERINGGIFT"],
    "wwm": ["WWMVIETNAM", "KIEMHIEP2025"]
}

TAROT_CARDS = [
    {"name": "The Fool", "meaning": "Khởi đầu mới, tự do, ngây thơ."},
    {"name": "The Magician", "meaning": "Sức mạnh ý chí, kỹ năng, sự tập trung."},
    {"name": "The Lovers", "meaning": "Tình yêu, sự hòa hợp, sự lựa chọn."},
    {"name": "Death", "meaning": "Kết thúc để bắt đầu, sự thay đổi lớn."},
    {"name": "The Sun", "meaning": "Thành công, niềm vui, năng lượng tích cực."},
]

# ================= HÀM HỖ TRỢ (HELPER FUNCTIONS) =================

def send_message(recipient_id, text):
    """Gửi tin nhắn văn bản"""
    params = {"access_token": ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    })
    r = requests.post("https://graph.facebook.com/v17.0/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        print(f"Lỗi gửi tin nhắn: {r.status_code} - {r.text}")

def send_image(recipient_id, image_url):
    """Gửi ảnh qua đường link"""
    params = {"access_token": ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "image",
                "payload": {"url": image_url, "is_reusable": True}
            }
        }
    })
    requests.post("https://graph.facebook.com/v17.0/me/messages", params=params, headers=headers, data=data)

def get_time_vn():
    """Lấy giờ Việt Nam"""
    tz_vn = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.datetime.now(tz_vn)

def handle_ai_command(user_id, command, args):
    """Xử lý logic từng lệnh"""
    response_text = ""
    
    try:
        # 1. /help
        if command == "/help":
            response_text = (
                "🤖 DANH SÁCH LỆNH BOT:\n"
                "1. /help: Xem hướng dẫn.\n"
                "2. /nhac [tên]: Nghe nhạc ngẫu nhiên hoặc tìm theo tên.\n"
                "3. /time: Xem giờ hiện tại (VN).\n"
                "4. /thptqg: Đếm ngược ngày thi THPTQG 2026.\n"
                "5. /wiki <câu hỏi>: Tra cứu Wikipedia.\n"
                "6. /gg <câu hỏi>: Tra Google.\n"
                "7. /code <tên game>: Lấy code game (genshin, hsr, wuwa...).\n"
                "8. /updt <tên game>: Kiểm tra phiên bản game.\n"
                "9. /meme: Xem ảnh chế Anime.\n"
                "10. /sticker: (Gửi kèm ảnh) Tạo sticker từ ảnh.\n"
                "11. /tarot <dd/mm/yyyy>: Bói bài Tarot.\n"
                "12. /hld: Xem ngày lễ sắp tới.\n"
                "13. /anime [tên]: Gợi ý hoặc tìm anime.\n"
                "14. /kbb: Chơi Kéo Búa Bao."
            )

        # 2. /nhac & 3. /nhac <tên>
        elif command == "/nhac":
            if not args:
                # Nhạc ngẫu nhiên (Link demo Youtube)
                songs = [
                    "https://www.youtube.com/watch?v=k5mX3NkA7jM", # Em của ngày hôm qua
                    "https://www.youtube.com/watch?v=0aF67n5rL8g"  # Đừng làm trái tim anh đau
                ]
                song = random.choice(songs)
                response_text = f"🎶 Bài nhạc ngẫu nhiên cho bạn: {song}"
            else:
                query = " ".join(args)
                response_text = f"🔎 Link tìm kiếm bài hát '{query}': https://www.youtube.com/results?search_query={query.replace(' ', '+')}"

        # 4. /time
        elif command == "/time":
            now = get_time_vn()
            response_text = now.strftime("🕒 Bây giờ là: %H:%M:%S - Ngày %d/%m/%Y (GMT+7)")

        # 5. /thptqg
        elif command == "/thptqg":
            target_date = datetime.datetime(2026, 6, 12, 0, 0, 0)
            now = datetime.datetime.now()
            diff = target_date - now
            if diff.days > 0:
                response_text = f"⏳ Còn {diff.days} ngày, {diff.seconds // 3600} giờ nữa là đến ngày 12/6/2026!"
            else:
                response_text = "Đã qua ngày thi THPTQG 2026 rồi!"

        # 6. /wiki
        elif command == "/wiki":
            if not args:
                response_text = "Vui lòng nhập từ khóa. Ví dụ: /wiki Hồ Chí Minh"
            else:
                try:
                    query = " ".join(args)
                    summary = wikipedia.summary(query, sentences=2)
                    response_text = f"📚 Wikipedia ({query}):\n{summary}"
                except wikipedia.exceptions.PageError:
                    response_text = "Không tìm thấy thông tin trên Wikipedia."
                except Exception:
                    response_text = "Có nhiều kết quả, vui lòng chi tiết hơn."

        # 7. /gg
        elif command == "/gg":
            if not args:
                response_text = "Vui lòng nhập câu hỏi. Ví dụ: /gg thời tiết hôm nay"
            else:
                query = " ".join(args)
                try:
                    # Lấy 1 kết quả đầu tiên
                    results = list(search(query, num_results=1, advanced=True))
                    if results:
                        first_res = results[0]
                        response_text = f"🔍 Google: {first_res.title}\n{first_res.description}\nLink: {first_res.url}"
                    else:
                        response_text = "Không tìm thấy kết quả nào."
                except Exception as e:
                    response_text = f"Lỗi tìm kiếm: {str(e)}"

        # 8. /code
        elif command == "/code":
            if not args:
                response_text = "Nhập tên game: genshin, hsr, wuwa, wwm..."
            else:
                game = args[0].lower()
                codes = GAME_CODES.get(game, ["Không tìm thấy code cho game này."])
                response_text = f"🎁 Code mới nhất cho {game.upper()}:\n" + "\n".join(codes)

        # 9. /updt
        elif command == "/updt":
            if not args:
                response_text = "Nhập tên game để xem update."
            else:
                game = args[0].lower()
                # Giả lập thông tin update
                response_text = f"📢 Thông tin cập nhật {game.upper()}: Phiên bản mới nhất đang được bảo trì hoặc đã sẵn sàng tải về. Hãy kiểm tra trang chủ game."

        # 10. /meme
        elif command == "/meme":
            # API meme anime public
            try:
                r = requests.get("https://meme-api.com/gimme/animememes")
                data = r.json()
                img_url = data.get("url")
                send_image(user_id, img_url)
                return # Đã gửi ảnh, thoát hàm
            except:
                response_text = "Lỗi khi lấy ảnh meme."

        # 11. /sticker
        elif command == "/sticker":
             # Lệnh này xử lý ở hàm main webhook nếu có ảnh đính kèm, ở đây chỉ báo lỗi nếu không có ảnh
             response_text = "Hãy gửi kèm một bức ảnh cùng với lệnh /sticker để tôi biến nó thành nhãn dán!"

        # 12. /tarot
        elif command == "/tarot":
            if not args:
                response_text = "Vui lòng nhập ngày sinh. Ví dụ: /tarot 01/01/2000"
            else:
                card = random.choice(TAROT_CARDS)
                response_text = f"🔮 Lá bài Tarot cho bạn:\n🃏 Tên: {card['name']}\n✨ Ý nghĩa: {card['meaning']}"

        # 13. /hld
        elif command == "/hld":
            # Tính toán ngày lễ gần nhất (Demo logic đơn giản)
            response_text = "🎉 Ngày lễ gần nhất: Tết Dương Lịch (01/01) hoặc Tết Nguyên Đán. Hãy chuẩn bị tinh thần nghỉ ngơi nhé!"

        # 14. /anime
        elif command == "/anime":
            anime_list = ["Naruto", "One Piece", "Attack on Titan", "Demon Slayer", "Frieren"]
            if not args:
                anime = random.choice(anime_list)
                response_text = f"🎬 Anime đề xuất: {anime}"
            else:
                name = " ".join(args)
                response_text = f"📺 Link xem '{name}': https://vuighe.net/tim-kiem/{name.replace(' ', '-')}"

        # 15. /kbb (Kéo Búa Bao)
        elif command == "/kbb":
            if user_id not in kbb_state:
                kbb_state[user_id] = "WAITING"
                response_text = "✊✌️✋ KÉO BÚA BAO!\nBot đã chọn và úp bài xuống (🎁).\nBạn hãy chat: 'kéo', 'búa', hoặc 'bao' để ra quyết định!"
            else:
                response_text = "Đang trong ván chơi, hãy ra 'kéo', 'búa' hoặc 'bao'."

        else:
            response_text = "Lệnh không hợp lệ. Gõ /help để xem danh sách."

    except Exception as e:
        response_text = f"⚠️ Đã xảy ra lỗi: {str(e)}"

    send_message(user_id, response_text)

def handle_kbb_logic(user_id, user_choice):
    """Xử lý logic game Kéo Búa Bao khi người dùng reply"""
    choices = ['kéo', 'búa', 'bao']
    if user_choice not in choices:
        return False # Không phải lượt chơi

    bot_choice = random.choice(choices)
    result = ""
    
    if user_choice == bot_choice:
        result = "Hòa rồi! 🤝"
    elif (user_choice == 'kéo' and bot_choice == 'bao') or \
         (user_choice == 'búa' and bot_choice == 'kéo') or \
         (user_choice == 'bao' and bot_choice == 'búa'):
        result = "Bạn thắng! 🎉"
    else:
        result = "Bot thắng! 🤖"

    msg = f"📦 Bot mở hộp quà: {bot_choice.upper()}\nBạn chọn: {user_choice.upper()}\n=> {result}"
    send_message(user_id, msg)
    del kbb_state[user_id] # Reset game
    return True

# ================= SERVER WEBHOOK =================

@app.route("/", methods=['GET'])
def verify():
    """Xác minh Webhook với Facebook"""
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args["hub.challenge"], 200
        return "Verification token mismatch", 403
    return "Hello world", 200

@app.route("/", methods=['POST'])
def webhook():
    """Nhận tin nhắn từ người dùng"""
    data = request.get_json()
    
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                # Lấy ID người gửi
                sender_id = messaging_event['sender']['id']
                
                # Bỏ qua tin nhắn delivery/read receipt
                if 'message' not in messaging_event:
                    continue

                message = messaging_event['message']
                
                # 1. Xử lý file ảnh (/sticker)
                if 'attachments' in message:
                    for att in message['attachments']:
                        if att['type'] == 'image':
                            # Nếu user vừa gửi ảnh và caption là /sticker (hoặc logic đơn giản là cứ gửi ảnh là bot gửi lại sticker)
                            # Ở đây ta check nếu không có text thì mặc định giả vờ làm sticker
                            img_url = att['payload']['url']
                            send_message(sender_id, "🖼️ Đang tạo sticker từ ảnh của bạn...")
                            send_image(sender_id, img_url) # Gửi lại chính ảnh đó (giả lập sticker)
                            return "ok", 200

                # 2. Xử lý văn bản
                if 'text' in message:
                    msg_text = message['text'].strip().lower()

                    # Kiểm tra xem có đang chơi Kéo Búa Bao không
                    if sender_id in kbb_state:
                        if handle_kbb_logic(sender_id, msg_text):
                            continue # Đã xử lý xong game
                    
                    # Phân tích lệnh (Ví dụ: /wiki Bác Hồ -> command=/wiki, args=['Bác', 'Hồ'])
                    if msg_text.startswith("/"):
                        parts = msg_text.split()
                        command = parts[0]
                        args = parts[1:]
                        
                        handle_ai_command(sender_id, command, args)
                    else:
                        # Chat thường (không phải lệnh)
                        send_message(sender_id, "Gõ /help để xem tôi có thể làm gì nhé!")

    return "ok", 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
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

