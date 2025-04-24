from PIL import Image, ImageDraw, ImageFont
import os

# Colors
CIRCLE_COLOR = (56, 189, 248, 255)     # Sky-400 (light blue)
BG_COLOR = (224, 242, 254, 255)         # Sky-100 (very light blue)
TEXT_COLOR = (255, 255, 255, 255)       # White
FONT_PATHS = [
    'arialbd.ttf', 'Arial Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
]

def find_font(font_paths, size):
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

def make_icon(size, out_path):
    img = Image.new('RGBA', (size, size), BG_COLOR)
    draw = ImageDraw.Draw(img)
    # Draw light blue circle
    draw.ellipse([(0, 0), (size - 1, size - 1)], fill=CIRCLE_COLOR)
    # Draw bold white K
    font_size = int(size * 0.7)
    font = find_font(FONT_PATHS, font_size)
    text = 'K'
    # Use textbbox for accurate sizing
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        w, h = font.getsize(text)
    draw.text(((size - w) / 2, (size - h) / 2 - size * 0.06), text, font=font, fill=TEXT_COLOR)
    img.save(out_path)

os.makedirs('frontend/public', exist_ok=True)
make_icon(192, 'frontend/public/icon-192.png')
make_icon(512, 'frontend/public/icon-512.png')
print('Kardosa icons generated.')
