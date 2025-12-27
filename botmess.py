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

# ================= 2. DỮ LIỆU & CẤU HÌNH =================

NUMBER_MAP = {
    "1": "/tarot", "2": "/baitay", "3": "/nhac", "4": "/time", "5": "/thptqg",
    "6": "/hld", "7": "/wiki", "8": "/gg", "9": "/kbb",
    "10": "/meme", "11": "/anime", "12": "/code",
    "13": "/updt", "14": "/leak", "15": "/banner", "16": "/sticker"
}

kbb_state = {} 
tarot_sessions = {} 

GAME_CODES = {
    "genshin": ["GENSHINGIFT", "CA3BLTURGH9D", "FATUI"],
    "hsr": ["STARRAILGIFT", "HSRVER10JRL", "POMPOM"],
    "wuwa": ["WUWA2024", "WUTHERINGGIFT"],
    "lq": ["LIENQUAN2025", "HPNY2025"],
    "bloxfruit": ["SUB2GAMERROBOT", "KITGAMING"]
}

# --- DỮ LIỆU TAROT 78 LÁ (FULL 100% CHI TIẾT) ---
MAJORS = {
    0: ("The Fool", "một sự khởi đầu đầy ngây thơ, tự do, dám chấp nhận rủi ro để bước vào hành trình mới"),
    1: ("The Magician", "năng lực hiện thực hóa ý tưởng, sự tập trung cao độ và kỹ năng làm chủ tình huống"),
    2: ("The High Priestess", "trực giác sâu sắc, những bí ẩn chưa được tiết lộ và thế giới nội tâm phong phú"),
    3: ("The Empress", "sự trù phú, vẻ đẹp của sự sáng tạo và tình yêu thương nuôi dưỡng"),
    4: ("The Emperor", "tính kỷ luật sắt đá, cấu trúc vững chắc, quyền lực và khả năng lãnh đạo"),
    5: ("The Hierophant", "niềm tin tâm linh, những giá trị truyền thống và sự học hỏi từ bậc thầy"),
    6: ("The Lovers", "sự lựa chọn quan trọng từ trái tim, tình yêu đôi lứa và sự kết nối sâu sắc"),
    7: ("The Chariot", "ý chí kiên cường, quyết tâm chiến thắng mọi trở ngại bằng sự kiểm soát"),
    8: ("Strength", "sức mạnh nội tâm, lòng trắc ẩn và khả năng kiểm soát bản năng bằng sự mềm mỏng"),
    9: ("The Hermit", "giai đoạn thu mình để chiêm nghiệm, tìm kiếm ánh sáng chân lý từ bên trong"),
    10: ("Wheel of Fortune", "sự xoay vần của định mệnh, những thay đổi bất ngờ mang tính bước ngoặt"),
    11: ("Justice", "sự công bằng, luật nhân quả và sự thật cần được phơi bày rõ ràng"),
    12: ("The Hanged Man", "sự hy sinh cần thiết, chấp nhận dừng lại để nhìn vấn đề ở góc độ khác"),
    13: ("Death", "một sự kết thúc để tái sinh, buông bỏ cái cũ kỹ để đón nhận cái mới mẻ"),
    14: ("Temperance", "sự cân bằng, chữa lành, kiên nhẫn hòa hợp các mặt đối lập"),
    15: ("The Devil", "những cám dỗ vật chất, sự ràng buộc độc hại hoặc đối mặt với bóng tối bên trong"),
    16: ("The Tower", "sự sụp đổ bất ngờ của những niềm tin cũ, một sự thức tỉnh mạnh mẽ và đau đớn"),
    17: ("The Star", "niềm hy vọng le lói nhưng bền bỉ, sự chữa lành sau tổn thương và niềm tin"),
    18: ("The Moon", "những nỗi lo âu tiềm thức, sự mơ hồ, ảo ảnh và những điều chưa rõ ràng"),
    19: ("The Sun", "niềm vui thuần khiết, sự thành công rực rỡ, năng lượng tích cực và sự rõ ràng"),
    20: ("Judgement", "tiếng gọi thức tỉnh, sự phán xét cuối cùng, tha thứ để tái sinh"),
    21: ("The World", "sự hoàn thành trọn vẹn, kết thúc một chu kỳ viên mãn để bước sang trang mới")
}

MINORS = {
    # WANDS (Gậy - Lửa - Hành động)
    "Ace of Wands": "một tia lửa cảm hứng bất ngờ, cơ hội mới đầy nhiệt huyết và đam mê bùng cháy",
    "Two of Wands": "lập kế hoạch cho tương lai, tầm nhìn xa và quyết định bước ra khỏi vùng an toàn",
    "Three of Wands": "sự mở rộng, chờ đợi kết quả từ những nỗ lực đã gieo trồng, nhìn ra thế giới rộng lớn",
    "Four of Wands": "niềm vui của sự sum họp, ăn mừng thành quả bước đầu, sự ổn định và hạnh phúc",
    "Five of Wands": "những cuộc tranh luận, mâu thuẫn hoặc cạnh tranh, nhưng là để rèn giũa bản lĩnh",
    "Six of Wands": "sự chiến thắng, vinh quang, được mọi người công nhận và tán thưởng",
    "Seven of Wands": "sự phòng thủ, kiên định bảo vệ lập trường của mình trước nhiều áp lực",
    "Eight of Wands": "mọi thứ diễn ra rất nhanh, tin tức đến dồn dập, hành động dứt khoát",
    "Nine of Wands": "sự kiên trì dù đã mệt mỏi, đề phòng và bảo vệ những gì mình đã xây dựng",
    "Ten of Wands": "gánh nặng trách nhiệm quá lớn, sự quá tải cần được san sẻ hoặc buông bỏ bớt",
    "Page of Wands": "một tin tức thú vị, sự tò mò khám phá và tinh thần phiêu lưu của tuổi trẻ",
    "Knight of Wands": "hành động bốc đồng, nhiệt huyết dâng trào nhưng đôi khi thiếu sự kiên nhẫn",
    "Queen of Wands": "sự tự tin, quyến rũ, năng lượng ấm áp và khả năng thu hút người khác",
    "King of Wands": "nhà lãnh đạo có tầm nhìn, người truyền cảm hứng và dám nghĩ dám làm",

    # CUPS (Cốc - Nước - Cảm xúc)
    "Ace of Cups": "một tình cảm mới chớm nở, trái tim rộng mở và trực giác nhạy bén",
    "Two of Cups": "sự kết nối đôi lứa, tình yêu hòa hợp hoặc một mối quan hệ đối tác ăn ý",
    "Three of Cups": "niềm vui của tình bạn, sự tụ tập ăn mừng và chia sẻ cảm xúc",
    "Four of Cups": "sự chán nản, thờ ơ với những cơ hội đang được đưa đến trước mắt",
    "Five of Cups": "nỗi buồn về những gì đã mất, sự tiếc nuối quá khứ mà quên đi hiện tại",
    "Six of Cups": "những ký ức ngọt ngào quay về, sự hoài niệm hoặc gặp lại người xưa",
    "Seven of Cups": "những ảo tưởng, quá nhiều lựa chọn mơ hồ và sự thiếu thực tế",
    "Eight of Cups": "sự dũng cảm bỏ lại những gì không còn phù hợp để đi tìm ý nghĩa thật sự",
    "Nine of Cups": "điều ước thành hiện thực, sự hài lòng và thỏa mãn về mặt cảm xúc",
    "Ten of Cups": "hạnh phúc viên mãn, gia đình êm ấm và sự trọn vẹn trong tình cảm",
    "Page of Cups": "một tin nhắn tình cảm, sự nhạy cảm, mơ mộng và trực giác ngây thơ",
    "Knight of Cups": "lời đề nghị lãng mạn, người sống theo cảm xúc và lý tưởng hóa tình yêu",
    "Queen of Cups": "sự thấu cảm sâu sắc, lòng trắc ẩn và khả năng chữa lành vết thương lòng",
    "King of Cups": "khả năng kiểm soát cảm xúc tuyệt vời, sự trưởng thành và bao dung",

    # SWORDS (Kiếm - Khí - Tư duy)
    "Ace of Swords": "một sự thật được phơi bày, trí tuệ sắc bén và quyết định lý trí dứt khoát",
    "Two of Swords": "sự bế tắc, do dự không dám nhìn thẳng vào sự thật, che giấu cảm xúc",
    "Three of Swords": "nỗi đau lòng, sự tổn thương sâu sắc do lời nói hoặc sự chia cắt",
    "Four of Swords": "thời gian cần thiết để nghỉ ngơi, hồi phục và tĩnh lặng sau bão tố",
    "Five of Swords": "một chiến thắng rỗng tuếch, sự mâu thuẫn và cái tôi quá lớn gây tổn thương",
    "Six of Swords": "sự rời bỏ những rắc rối để chuyển đến một nơi bình yên hơn, sự chữa lành chậm rãi",
    "Seven of Swords": "sự lén lút, chiến thuật không trung thực hoặc cố gắng trốn tránh trách nhiệm",
    "Eight of Swords": "cảm giác bị trói buộc, bế tắc do chính suy nghĩ tiêu cực của bản thân tạo ra",
    "Nine of Swords": "nỗi lo âu, mất ngủ, ác mộng và sự căng thẳng tột độ về tinh thần",
    "Ten of Swords": "sự kết thúc đau đớn nhưng dứt khoát, chạm đáy để bắt đầu đi lên",
    "Page of Swords": "sự tò mò, quan sát sắc bén, nhưng đôi khi là tin tức thị phi",
    "Knight of Swords": "hành động vội vã, lời nói thẳng thắn đến mức gây sát thương",
    "Queen of Swords": "sự sắc sảo, độc lập, phán xét công bằng và không để cảm xúc chi phối",
    "King of Swords": "quyền lực của trí tuệ, sự công minh, nghiêm khắc và tư duy logic",

    # PENTACLES (Tiền - Đất - Vật chất)
    "Ace of Pentacles": "cơ hội tài chính mới, sự khởi đầu thịnh vượng và nền tảng vững chắc",
    "Two of Pentacles": "sự cân bằng giữa các yếu tố, khả năng xoay sở linh hoạt trong khó khăn",
    "Three of Pentacles": "sự hợp tác làm việc nhóm, kỹ năng chuyên môn được công nhận",
    "Four of Pentacles": "sự giữ của, kiểm soát tài chính chặt chẽ, đôi khi là keo kiệt",
    "Five of Pentacles": "sự thiếu thốn vật chất, cảm giác bị bỏ rơi hoặc khó khăn tạm thời",
    "Six of Pentacles": "sự cho và nhận, lòng hào phóng hoặc sự cân bằng trong tài chính",
    "Seven of Pentacles": "sự kiên nhẫn chờ đợi thu hoạch, đánh giá lại quá trình đầu tư",
    "Eight of Pentacles": "sự chăm chỉ, tỉ mỉ rèn luyện kỹ năng, làm việc cật lực",
    "Nine of Pentacles": "sự độc lập tài chính, tận hưởng thành quả lao động, sự sang trọng",
    "Ten of Pentacles": "sự giàu có bền vững, di sản gia đình và sự sung túc trọn vẹn",
    "Page of Pentacles": "ham học hỏi kiến thức mới, tin tức tốt về tiền bạc, sự thực tế",
    "Knight of Pentacles": "sự cần cù, đáng tin cậy, làm việc chậm nhưng chắc chắn",
    "Queen of Pentacles": "sự chăm sóc, quản lý tài chính tài tình, người phụ nữ thực tế",
    "King of Pentacles": "đỉnh cao của thành công vật chất, doanh nhân thành đạt, sự giàu có"
}

SPREADS_TAROT = {
    "1": {"name": "1 Lá (Thông điệp)", "count": 1, "pos": ["Lời khuyên chính"]},
    "3": {"name": "3 Lá (QK-HT-TL)", "count": 3, "pos": ["Quá khứ", "Hiện tại", "Tương lai"]},
    "5": {"name": "5 Lá (Chi tiết)", "count": 5, "pos": ["Vấn đề hiện tại", "Thách thức", "Gốc rễ vấn đề", "Lời khuyên", "Kết quả tiềm năng"]}
}

# --- DỮ LIỆU BÀI TÂY 52 LÁ (VĂN PHONG STORYTELLING) ---
PLAYING_CARDS_DATA = {
    "Hearts": { # Cơ
        "A": "một tình yêu mới chớm nở hoặc niềm hạnh phúc gia đình ấm áp",
        "K": "một người đàn ông giàu tình cảm, chân thành và tốt bụng",
        "Q": "một người phụ nữ dịu dàng, thấu hiểu và đáng tin cậy",
        "J": "những tin tức vui vẻ về tình cảm hoặc một người trẻ tuổi lãng mạn",
        "10": "hạnh phúc viên mãn, sự trọn vẹn trong mối quan hệ (có thể là hỷ sự)",
        "9": "điều ước của bạn đang dần trở thành hiện thực",
        "8": "những cuộc gặp gỡ, hẹn hò và giao lưu vui vẻ",
        "7": "cảm giác ghen tuông, bất an hoặc những kỳ vọng quá cao",
        "6": "người cũ hoặc những kỷ niệm xưa cũ quay trở lại",
        "5": "một chút nỗi buồn thoáng qua hoặc sự thất vọng trong tình cảm",
        "4": "sự ổn định, cam kết, nhưng đôi khi hơi thiếu lửa",
        "3": "sự phân vân giữa các lựa chọn hoặc có người thứ ba xen vào",
        "2": "sự kết đôi, sự hòa hợp tuyệt vời giữa hai tâm hồn"
    },
    "Diamonds": { # Rô
        "A": "một cơ hội tài chính mới hoặc tin tức giấy tờ quan trọng",
        "K": "người đàn ông thành đạt, có quyền lực về tài chính",
        "Q": "người phụ nữ sắc sảo, quản lý chi tiêu rất giỏi",
        "J": "tin tức về tiền bạc, lợi nhuận hoặc công việc mới",
        "10": "sự thịnh vượng, dòng tiền lớn hoặc thành công rực rỡ",
        "9": "sự tự chủ tài chính, thoải mái chi tiêu không lo nghĩ",
        "8": "quá trình nỗ lực học hỏi, rèn luyện kỹ năng kiếm tiền",
        "7": "cảnh báo rủi ro đầu tư hoặc những tin đồn thất thiệt",
        "6": "sự giúp đỡ về vật chất, vay mượn hoặc làm từ thiện",
        "5": "những khoản chi tiêu ngoài ý muốn hoặc khó khăn tạm thời",
        "4": "sự tiết kiệm, giữ chặt tài sản, ưu tiên an toàn",
        "3": "sự hợp tác làm ăn, đầu tư chung vốn sinh lời",
        "2": "việc ký kết hợp đồng, trao đổi mua bán thuận lợi"
    },
    "Clubs": { # Tép
        "A": "sự khởi đầu của một dự án, công việc hoặc ý tưởng mới",
        "K": "người sếp, lãnh đạo có tầm nhìn và chuyên môn cao",
        "Q": "người phụ nữ thông minh, khéo léo trong giao tiếp công việc",
        "J": "sự nhiệt huyết của tuổi trẻ, nhân viên mới hoặc người học việc",
        "10": "thành công lớn trong sự nghiệp, thăng chức hoặc đạt mục tiêu",
        "9": "tham vọng lớn lao nhưng đi kèm áp lực công việc nặng nề",
        "8": "tin tức đến rất nhanh, những chuyến đi công tác, di chuyển",
        "7": "những cuộc tranh luận, mâu thuẫn quan điểm với đồng nghiệp",
        "6": "cơ hội phát triển, sự ghi nhận công sức xứng đáng",
        "5": "sự thay đổi môi trường làm việc hoặc thử thách mới cần vượt qua",
        "4": "nền tảng sự nghiệp vững chắc, sự ổn định lâu dài",
        "3": "giai đoạn cân nhắc, đứng trước nhiều ngã rẽ sự nghiệp",
        "2": "sự hỗ trợ đắc lực từ đối tác, làm việc nhóm hiệu quả"
    },
    "Spades": { # Bích
        "A": "một sự kết thúc dứt khoát để bắt đầu lại (hoặc vấn đề giấy tờ pháp lý)",
        "K": "người đàn ông nghiêm khắc, lạnh lùng, giải quyết bằng lý trí",
        "Q": "người phụ nữ sắc sảo nhưng cô độc, đa nghi",
        "J": "kẻ tiểu nhân, tin tức không vui hoặc sự dối trá",
        "10": "gánh nặng tâm lý, áp lực tột độ hoặc chuyện xui rủi",
        "9": "nỗi lo âu, mất ngủ, căng thẳng kéo dài",
        "8": "những trở ngại bất ngờ, cảm giác bị bế tắc",
        "7": "sự phản bội, đâm sau lưng hoặc lừa gạt",
        "6": "sự rời bỏ, trốn tránh hoặc đi xa để tìm bình yên",
        "5": "sự thất bại, mất mát hoặc đổ vỡ một kế hoạch",
        "4": "sự trì hoãn, mệt mỏi về thể chất cần nghỉ ngơi",
        "3": "sự chia ly, đau lòng hoặc những rạn nứt tình cảm",
        "2": "mâu thuẫn trực diện, cãi vã căng thẳng"
    }
}

SPREADS_PLAYING = {
    "3": {"name": "3 Lá (QK-HT-TL)", "count": 3, "pos": ["Quá khứ ảnh hưởng", "Hiện tại", "Xu hướng tương lai"]},
    "5": {"name": "5 Lá (Tổng quan)", "count": 5, "pos": ["Vấn đề chính", "Nguyên nhân sâu xa", "Yếu tố tiềm ẩn", "Lời khuyên hành động", "Kết quả dự báo"]},
    "7": {"name": "7 Lá (Tình duyên)", "count": 7, "pos": ["Năng lượng của bạn", "Năng lượng đối phương", "Cảm xúc của bạn", "Cảm xúc của họ", "Trở ngại khách quan", "Trở ngại chủ quan", "Kết quả mối quan hệ"]}
}

# ================= 3. HÀM HỖ TRỢ =================

def send_text(user_id, text):
    try: requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers={"Content-Type": "application/json"}, data=json.dumps({"recipient": {"id": user_id}, "message": {"text": text}}))
    except: pass

def send_typing(user_id):
    try: requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers={"Content-Type": "application/json"}, data=json.dumps({"recipient": {"id": user_id}, "sender_action": "typing_on"}))
    except: pass

def send_image(user_id, url):
    try: requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers={"Content-Type": "application/json"}, data=json.dumps({"recipient": {"id": user_id}, "message": {"attachment": {"type": "image", "payload": {"url": url, "is_reusable": True}}}}))
    except: pass

def send_quick_reply(user_id, text, options):
    q_replies = [{"content_type": "text", "title": t, "payload": p} for t, p in options]
    try: requests.post(f"https://graph.facebook.com/v17.0/me/messages?access_token={ACCESS_TOKEN}", headers={"Content-Type": "application/json"}, data=json.dumps({"recipient": {"id": user_id}, "messaging_type": "RESPONSE", "message": {"text": text, "quick_replies": q_replies}}))
    except: pass

def search_text_summary(query):
    try:
        with DDGS() as ddgs:
            res = list(ddgs.text(query, max_results=1))
            return f"📌 **{res[0]['title']}**\n\n📝 {res[0]['body']}\n\n🔗 Nguồn: {res[0]['href']}" if res else "Không tìm thấy."
    except: return "Lỗi tìm kiếm."

def search_image_url(query):
    try:
        with DDGS() as ddgs:
            res = list(ddgs.images(query, max_results=1))
            return res[0]['image'] if res else None
    except: return None

# ================= 4. ENGINE TAROT (VĂN PHONG CHỮA LÀNH) =================

def generate_tarot_deck():
    deck = []
    # Major Arcana
    for i, (n, m) in MAJORS.items():
        deck.append({"name": f"{n} (Major)", "meaning": m, "type": "Major"})
    # Minor Arcana (Dữ liệu chi tiết 56 lá)
    for name, meaning in MINORS.items():
        deck.append({"name": name, "meaning": meaning, "type": "Minor"})
    return deck

def execute_tarot_reading(ctx):
    deck = generate_tarot_deck()
    random.shuffle(deck)
    spread = SPREADS_TAROT.get(ctx.get("spread_id", "3"), SPREADS_TAROT["3"])
    drawn = []
    for i in range(spread["count"]):
        if not deck: break
        c = deck.pop()
        c["pos"] = spread["pos"][i]
        c["orientation"] = random.choice(["Xuôi", "Ngược"])
        drawn.append(c)

    # Viết văn
    msg = f"🔮 **KẾT QUẢ TAROT: {ctx.get('topic').upper()}**\n"
    msg += f"👤 Querent: {ctx.get('info', 'Ẩn danh')}\n➖➖➖➖➖➖\n\n"
    msg += "🍃 **DIỄN GIẢI CHI TIẾT:**\n\n"
    
    for i, c in enumerate(drawn):
        prefix = ["Mở đầu,", "Tiếp theo,", "Sau đó,", "Cuối cùng,"][min(i, 3)]
        status = f" ({c['orientation']})"
        msg += f"🔸 **{c['pos']}**: {c['name']}{status}\n"
        msg += f"{prefix} lá bài này mang đến thông điệp về {c['meaning']}. "
        if c['orientation'] == "Ngược":
            msg += "Tuy nhiên, ở chiều ngược, năng lượng này đang bị tắc nghẽn hoặc cần bạn nhìn nhận lại từ bên trong.\n\n"
        else:
            msg += "Đây là một tín hiệu thuận lợi để bạn phát huy.\n\n"
            
    msg += "💡 **LỜI KHUYÊN TỪ VŨ TRỤ:**\n"
    msg += "Hãy hít thở sâu và đón nhận thông điệp này. Mọi thứ diễn ra đều có lý do của nó, và bạn luôn có quyền năng để kiến tạo tương lai của mình."
    return msg

# ================= 5. ENGINE BÀI TÂY (VĂN PHONG STORYTELLING & LOGIC CAO CẤP) =================

def generate_playing_deck():
    deck = []
    suits = {"Hearts": "♥ Cơ", "Diamonds": "♦ Rô", "Clubs": "♣ Tép", "Spades": "♠ Bích"}
    ranks = {"A":"Át", "2":"Hai", "3":"Ba", "4":"Bốn", "5":"Năm", "6":"Sáu", "7":"Bảy", "8":"Tám", "9":"Chín", "10":"Mười", "J":"Bồi", "Q":"Đầm", "K":"Già"}
    for s_en, meaning_dict in PLAYING_CARDS_DATA.items():
        for r, m in meaning_dict.items():
            deck.append({"name": f"{ranks[r]} {suits[s_en][2:]}", "symbol": f"{r}{suits[s_en][0]}", "suit": s_en, "meaning": m})
    return deck

def analyze_card_context(card, topic, position):
    """Hàm tạo văn phong phân tích (Storytelling)"""
    topic = topic.lower()
    suit = card["suit"]
    meaning = card["meaning"]
    
    analysis = ""
    
    # 1. Phân tích lá bài theo ngữ cảnh (Context-Aware)
    if "tình" in topic:
        if suit == "Hearts": analysis = f"Lá {card['name']} thuộc nước Cơ, rất vượng về tình cảm. Nó báo hiệu {meaning.lower()}."
        elif suit == "Diamonds": analysis = f"Lá {card['name']} thuộc nước Rô (Tiền bạc). Điều này cho thấy vấn đề tài chính hoặc thực tế đang tác động mạnh đến chuyện tình cảm. Cụ thể là {meaning.lower()}."
        elif suit == "Clubs": analysis = f"Lá {card['name']} thuộc nước Tép (Công việc). Có vẻ như sự bận rộn hoặc áp lực công việc đang làm xao nhãng mối quan hệ. ({meaning})."
        elif suit == "Spades": analysis = f"Lá {card['name']} thuộc nước Bích. Đây là dấu hiệu của thử thách tâm lý hoặc rào cản. {meaning}."
    
    elif "tiền" in topic or "công" in topic:
        if suit == "Diamonds" or suit == "Clubs": analysis = f"Lá {card['name']} rất tốt cho công việc/tiền bạc. Nó mang ý nghĩa về {meaning.lower()}."
        elif suit == "Hearts": analysis = f"Lá {card['name']} thuộc nước Cơ. Bạn đang để cảm xúc chi phối các quyết định lý trí. {meaning}."
        elif suit == "Spades": analysis = f"Lá {card['name']} cảnh báo rủi ro hoặc khó khăn. {meaning}."
        
    else: # Tổng quan
        analysis = f"Lá {card['name']} mang thông điệp: {meaning}."

    # 2. Phân tích theo vị trí (Position-Based)
    if "Vấn đề" in position:
        return f"Hiện tại, {analysis.lower().replace('lá ', '')} Đây là nút thắt chính bạn cần gỡ bỏ."
    elif "Nguyên nhân" in position:
        return f"Nguyên nhân sâu xa dẫn đến việc này là do {analysis.lower().replace('lá ', '')}"
    elif "Lời khuyên" in position:
        return f"Lời khuyên cho bạn lúc này: Hãy lưu ý đến thông điệp của {card['name']}. {analysis}"
    elif "Kết quả" in position:
        return f"Nếu đi đúng hướng, kết quả sẽ là: {analysis}"
    else:
        return f"Ở khía cạnh '{position}', lá bài chỉ ra rằng: {analysis}"

def execute_playing_reading(user_context):
    deck = generate_playing_deck()
    random.shuffle(deck)
    spread = SPREADS_PLAYING.get(user_context.get("spread_id", "5"), SPREADS_PLAYING["5"])
    topic = user_context.get("topic", "Tổng quan")
    
    drawn = []
    for i in range(spread["count"]):
        if not deck: break
        c = deck.pop()
        c["pos_name"] = spread["pos"][i]
        drawn.append(c)
        
    # --- XÂY DỰNG VĂN BẢN TRẢ LỜI ---
    msg = f"🎭 **KẾT QUẢ BÓI BÀI TÂY**\n"
    msg += f"👤 Querent: {user_context.get('info', 'Ẩn danh')}\n"
    msg += f"❓ Vấn đề: **{topic}**\n"
    msg += f"🔀 Kiểu trải: {spread['name']}\n"
    msg += "➖➖➖➖➖➖➖➖➖➖\n\n"
    
    # 1. Danh sách bài
    msg += "🃏 **CÁC LÁ BÀI ĐƯỢC BỐC:**\n"
    for c in drawn: msg += f"• {c['symbol']} – {c['name']}\n"
    msg += "\n🔍 **LUẬN GIẢI CHI TIẾT:**\n"
    
    # 2. Phân tích từng lá (Dùng hàm thông minh)
    for i, c in enumerate(drawn):
        explanation = analyze_card_context(c, topic, c['pos_name'])
        msg += f"🔹 **Lá {i+1} – {c['symbol']} ({c['pos_name']})**\n{explanation}\n\n"
        
    # 3. Tổng kết (Logic đếm chất)
    suits_count = {"Hearts": 0, "Diamonds": 0, "Clubs": 0, "Spades": 0}
    for c in drawn: suits_count[c["suit"]] += 1
    dom_suit = max(suits_count, key=suits_count.get)
    
    msg += "✅ **TỔNG KẾT:**\n"
    if dom_suit == "Hearts": msg += "Trải bài thiên về tình cảm. Mọi việc sẽ được giải quyết êm đẹp nếu bạn dùng sự chân thành."
    elif dom_suit == "Diamonds": msg += "Trải bài nặng về vật chất. Hãy thực tế, tính toán lợi ích rõ ràng."
    elif dom_suit == "Clubs": msg += "Trải bài thiên về hành động. Đừng chần chừ, hãy làm ngay đi."
    elif dom_suit == "Spades": msg += "Trải bài nhiều thử thách. Hãy cẩn trọng, án binh bất động lúc này."
    
    msg += "\n\n💡 **LỜI KHUYÊN:** Đừng quá lo lắng nếu gặp lá xấu. Bài Tây chỉ ra xu hướng, còn bạn nắm quyền quyết định."
    return msg

# ================= 6. QUY TRÌNH HỘI THOẠI =================

def handle_flow(user_id, text, payload):
    s = tarot_sessions.get(user_id)
    if not s: return
    
    # Anti-Reset
    if payload and "SPREAD_" in payload:
        sid = payload.replace("SPREAD_", "")
        s["spread_id"] = sid
        send_typing(user_id)
        if s.get("mode") == "TAROT":
            send_text(user_id, "🔀 Đang xào bài Tarot... (Tập trung nhé)...")
            res = execute_tarot_reading(s)
        else:
            send_text(user_id, "🔀 Đang xào bài Tây... (Cắt bài 3 phần)...")
            res = execute_playing_reading(s)
        send_text(user_id, res)
        if user_id in tarot_sessions: del tarot_sessions[user_id]
        return

    if s["step"] == 1:
        s["topic"] = payload if payload else text
        s["step"] = 2
        send_text(user_id, f"Bạn muốn hỏi cụ thể gì về '{s['topic']}'? (Gõ '.' để bỏ qua)")
        return

    if s["step"] == 2:
        s["question"] = text
        s["step"] = 3
        send_quick_reply(user_id, "Ngày sinh/Cung hoàng đạo?", [("Bỏ qua", "SKIP")])
        return

    if s["step"] == 3:
        s["info"] = text
        s["step"] = 4
        if s.get("mode") == "TAROT":
            ops = [("1 Lá", "SPREAD_1"), ("3 Lá", "SPREAD_3"), ("5 Lá", "SPREAD_5")]
            send_quick_reply(user_id, "🔹 Chọn trải bài Tarot:", ops)
        else:
            ops = [("3 Lá (Thời gian)", "SPREAD_3"), ("5 Lá (Tổng quan)", "SPREAD_5"), ("7 Lá (Tình duyên)", "SPREAD_7")]
            send_quick_reply(user_id, "🔹 Chọn trải bài Tây:", ops)
        return

# ================= 7. XỬ LÝ LỆNH =================

def handle_command(user_id, cmd, args):
    cmd = cmd.lower()
    
    if cmd == "/tarot":
        tarot_sessions[user_id] = {"step": 1, "mode": "TAROT"}
        send_quick_reply(user_id, "🔮 **PHÒNG TAROT ONLINE**\nChủ đề bạn quan tâm?", [("Tình yêu", "Tình yêu"), ("Công việc", "Công việc"), ("Tài chính", "Tài chính")])

    elif cmd == "/baitay":
        tarot_sessions[user_id] = {"step": 1, "mode": "PLAYING"}
        send_quick_reply(user_id, "🎭 **PHÒNG BÓI BÀI TÂY**\nBạn muốn xem về?", [("Tình cảm", "Tình cảm"), ("Tiền bạc", "Tiền bạc"), ("Công việc", "Công việc")])

    elif cmd == "/nhac":
        q = " ".join(args) if args else ""
        link = f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}" if q else "https://www.youtube.com/watch?v=k5mX3NkA7jM"
        send_text(user_id, f"🎧 **NHẠC HAY:** {link}")

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
                s = wikipedia.summary(" ".join(args), sentences=3)
                send_text(user_id, f"📚 **WIKI:**\n{s}")
            except: send_text(user_id, "❌ Không tìm thấy.")

    elif cmd == "/gg":
        if not args: send_text(user_id, "🌐 Nhập câu hỏi.")
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
        if not args: send_text(user_id, "🆕 Nhập tên game.")
        else:
            q = " ".join(args)
            send_typing(user_id)
            res = search_text_summary(f"{q} latest update patch notes summary")
            send_text(user_id, f"🆕 **UPDATE {q.upper()}:**\n\n{res}")

    elif cmd == "/leak":
        if not args: send_text(user_id, "🕵️ Nhập tên game.")
        else:
            q = " ".join(args)
            send_typing(user_id)
            res = search_text_summary(f"{q} latest leaks rumors")
            send_text(user_id, f"🕵️ **LEAK {q.upper()}:**\n\n{res}")

    elif cmd == "/banner":
        if not args: send_text(user_id, "🏷️ Nhập tên game.")
        else:
            q = " ".join(args)
            send_typing(user_id)
            now = datetime.datetime.now().strftime('%B %Y')
            info = search_text_summary(f"current limited banner {q} {now}")
            img = search_image_url(f"{q} current banner {now} official")
            send_text(user_id, f"🏷️ **BANNER:**\n{info}")
            if img: send_image(user_id, img)

    elif cmd == "/sticker":
        send_text(user_id, "🖼️ Gửi ảnh vào đây để tạo sticker.")

    elif cmd in ["/help", "menu", "hi"]:
        menu = (
            "✨➖ 🤖 **DANH SÁCH LỆNH BOT** 🤖➖✨\n"
            "                      Tronglv📸\n"
            "➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
            "    🔮 **TAROT & TÂM LINH**\n"
            "✨ 1./tarot : Bói bài Tarot\n"
            "🎭 2./baitay : Bói bài Tây\n\n"
            "    🎵 **ÂM NHẠC**\n"
            "🎧 3./nhac [tên] : Tìm nhạc Youtube\n\n"
            "    🕒 **THỜI GIAN & SỰ KIỆN**\n"
            "⏰ 4./time : Xem giờ hiện tại\n"
            "⏳ 5./thptqg : Đếm ngược ngày thi\n"
            "🎉 6./hld : Ngày lễ sắp tới\n\n"
            "    📚 **TRA CỨU**\n"
            "📖 7./wiki [từ] : Tra Wikipedia\n"
            "🌐 8./gg [câu hỏi] : Link Google\n\n"
            "    🎮 **GIẢI TRÍ**\n"
            "✊ 9./kbb : Chơi Kéo Búa Bao\n"
            "🤣 10./meme : Xem ảnh chế\n"
            "🎬 11./anime : Gợi ý Anime\n\n"
            "    🎁 **GAME**\n"
            "🎟️ 12./code [game] : Giftcode game\n"
            "🆕 13./updt [game] : Thông tin update\n"
            "🕵️ 14./leak [game] : Tổng hợp leak\n"
            "🏷️ 15./banner [game] : Banner hiện tại\n\n"
            "    🖼️ **HÌNH ẢNH**\n"
            "🖌️ 16./sticker : Gửi ảnh để tạo sticker"
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
                        handle_flow(sender_id, text, payload)
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
                        else: send_text(sender_id, "Gõ /help hoặc số 1-16.")

        return "ok", 200
    except: return "ok", 200

if __name__ == "__main__":
    app.run(port=5000)
