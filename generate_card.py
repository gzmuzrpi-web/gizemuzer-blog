#!/usr/bin/env python3
"""
generate_card.py - Creates high-resolution, pixel-perfect 1080x1080 Instagram quote cards
with Gizem's authentic quotes, elegant typography, and website branding.
"""

from PIL import Image, ImageDraw, ImageFont
import textwrap
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "static" / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Color Palette (Exact match to gizemuzer.xyz warm beige theme)
COLOR_BG = (245, 240, 230)        # #F5F0E6 Warm Beige
COLOR_BORDER = (223, 215, 197)    # #DFD7C5
COLOR_TEXT = (43, 36, 32)         # #2B2420 Deep Walnut
COLOR_MUTED = (115, 102, 93)      # #73665D Warm Taupe
COLOR_TERRACOTTA = (184, 98, 54)  # #B86236 Terracotta
COLOR_FOREST = (44, 83, 64)       # #2C5340 Forest Sage
COLOR_WHITE = (253, 251, 247)

FONT_SERIF = "/System/Library/Fonts/Supplemental/Georgia.ttf"
FONT_SERIF_ITALIC = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
FONT_SERIF_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
FONT_SANS = "/System/Library/Fonts/HelveticaNeue.ttc"

def create_quote_card(quote_lines, author, essay_title, filename, badge="SATIR ARASI • DENEMELER"):
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), COLOR_BG)
    draw = ImageDraw.Draw(img)

    # 1. Elegant Double Frame
    # Outer margin
    m = 50
    draw.rectangle([m, m, W - m, H - m], outline=COLOR_BORDER, width=2)
    # Inner subtle line
    m2 = 60
    draw.rectangle([m2, m2, W - m2, H - m2], outline=(235, 228, 212), width=1)

    # 2. Header Badge
    try:
        font_badge = ImageFont.truetype(FONT_SANS, 22)
    except:
        font_badge = ImageFont.load_default()
    
    # Draw tiny terracotta dot
    dot_x = W // 2 - 130
    draw.ellipse([dot_x, 115, dot_x + 8, 123], fill=COLOR_TERRACOTTA)
    draw.text((dot_x + 20, 110), badge, fill=COLOR_MUTED, font=font_badge)

    # 3. Large Decorative Quote Mark
    try:
        font_quote_mark = ImageFont.truetype(FONT_SERIF, 130)
    except:
        font_quote_mark = ImageFont.load_default()
    draw.text((120, 190), "“", fill=COLOR_TERRACOTTA, font=font_quote_mark)

    # 4. Main Quote Text (Centered & Beautifully spaced)
    try:
        font_quote = ImageFont.truetype(FONT_SERIF_ITALIC, 42)
    except:
        font_quote = ImageFont.load_default()

    # Wrap and calculate text height
    wrapped_lines = []
    for paragraph in quote_lines:
        lines = textwrap.wrap(paragraph, width=34)
        wrapped_lines.extend(lines)
        wrapped_lines.append("") # paragraph break

    if wrapped_lines and wrapped_lines[-1] == "":
        wrapped_lines.pop()

    line_height = 68
    total_text_h = len(wrapped_lines) * line_height
    start_y = 350 + (320 - total_text_h) // 2

    cur_y = start_y
    for line in wrapped_lines:
        if line == "":
            cur_y += 30
            continue
        bbox = draw.textbbox((0, 0), line, font=font_quote)
        line_w = bbox[2] - bbox[0]
        x = (W - line_w) // 2
        draw.text((x, cur_y), line, fill=COLOR_TEXT, font=font_quote)
        cur_y += line_height

    # 5. Decorative Horizontal Divider
    div_y = 780
    draw.line([(W // 2 - 60), div_y, (W // 2 + 60), div_y], fill=COLOR_TERRACOTTA, width=2)

    # 6. Author & Essay
    try:
        font_author = ImageFont.truetype(FONT_SERIF_BOLD, 28)
        font_essay = ImageFont.truetype(FONT_SERIF_ITALIC, 22)
        font_url = ImageFont.truetype(FONT_SANS, 24)
    except:
        font_author = font_essay = font_url = ImageFont.load_default()

    # Author
    bbox_auth = draw.textbbox((0, 0), author, font=font_author)
    draw.text(((W - (bbox_auth[2] - bbox_auth[0])) // 2, 815), author, fill=COLOR_TEXT, font=font_author)

    # Essay title
    bbox_essay = draw.textbbox((0, 0), essay_title, font=font_essay)
    draw.text(((W - (bbox_essay[2] - bbox_essay[0])) // 2, 855), essay_title, fill=COLOR_MUTED, font=font_essay)

    # 7. Bottom Callout Button (gizemuzer.xyz)
    btn_w, btn_h = 360, 54
    btn_x = (W - btn_w) // 2
    btn_y = 920
    # Forest green pill button
    draw.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=27, fill=COLOR_FOREST)
    
    url_text = "Yazının devamı ➔ gizemuzer.xyz"
    bbox_url = draw.textbbox((0, 0), url_text, font=font_url)
    url_w = bbox_url[2] - bbox_url[0]
    draw.text((btn_x + (btn_w - url_w) // 2, btn_y + 14), url_text, fill=COLOR_WHITE, font=font_url)

    out_path = OUTPUT_DIR / filename
    img.save(out_path, quality=95)
    print(f"✅ Görsel oluşturuldu: {out_path}")

if __name__ == "__main__":
    # Card 1: Başkasının ayakkabısı alıntısı
    create_quote_card(
        quote_lines=[
            "“Başkalarının ayakkabısıyla yürürken onların hızıyla ilerler, onların yolundaki manzaraya razı olursunuz.",
            "Kendi hislerinizin size söylediklerini duyabilmek için önce o ayakkabıları çıkarmalısınız.”"
        ],
        author="Gizem Uzer",
        essay_title="Kendi Yuvanı Örmek: Başkalarının Aynasında Kaybolan Sezgiler",
        filename="instagram_quote_card_1.jpg"
    )

    # Card 2: Kusurun ışığı alıntısı
    create_quote_card(
        quote_lines=[
            "“Oysa kusurum bana ne güzel bir kapı aralamıştı...",
            "Birine ayna olacaksanız, yalnızca onun ışığına değil; karanlığına da ayna olmalısınız.”"
        ],
        author="Gizem Uzer",
        essay_title="Kusurun Işığı ve Aynanın İki Yüzü",
        filename="instagram_quote_card_2.jpg"
    )
