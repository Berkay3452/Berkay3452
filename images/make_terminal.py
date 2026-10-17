"""Terminal temalı karşılama GIF'i (Claude Design 'C · Terminal' tasarımı).
Çalıştır:  python images/make_terminal.py   ->  images/hello-terminal.gif
Gerekli:   pip install pillow   (Windows'ta Cascadia Mono yazı tipi kullanılır)
"""
from PIL import Image, ImageDraw, ImageFont

W, H, S = 880, 220, 2
BG, PANEL = (13, 17, 23), (11, 16, 32)
CYAN, PINK, GRAY, TEXT = (34, 211, 238), (244, 114, 182), (125, 133, 144), (230, 237, 243)
FONT = "C:/Windows/Fonts/CascadiaMono.ttf"

def font(size, bold):
    f = ImageFont.truetype(FONT, size * S)
    try:
        f.set_variation_by_name("Bold" if bold else "Regular")
    except Exception:
        pass
    return f

f1, f2 = font(21, False), font(40, True)

# (metin, renk, yazı tipi) parçaları, satır başına
L1 = [("~/berkay", CYAN, f1), (" ", GRAY, f1), ("$", PINK, f1), (' echo "Hello, Coders"', GRAY, f1)]
L2 = [(">", PINK, f2), (" ", TEXT, f2), ("I'm Berkay Öztürk", TEXT, f2)]
X0 = (W - 780) // 2 + 38          # panel içi sol boşluk
Y1, Y2 = 78, 112                   # satır üst konumları (px)

def chars(line, x0):
    out, x = [], x0 * S
    for text, col, f in line:
        for ch in text:
            out.append((ch, col, f, x))
            x += f.getlength(ch)
    return out, x

C1, END1 = chars(L1, X0)
C2, END2 = chars(L2, X0)

def base():
    img = Image.new("RGB", (W * S, H * S), BG)
    # degrade çerçeve (cyan -> mor -> pembe)
    px0, py0, px1, py1 = (W - 780) // 2 * S, 35 * S, (W + 780) // 2 * S, 185 * S
    grad = Image.new("RGB", (W * S, H * S))
    gd = ImageDraw.Draw(grad)
    stops = [(34, 211, 238), (130, 80, 223), (244, 114, 182)]
    for x in range(px0, px1):
        t = (x - px0) / (px1 - px0) * 2
        i = min(int(t), 1); u = t - i
        gd.line([(x, py0), (x, py1)], fill=tuple(int(stops[i][k] + (stops[i + 1][k] - stops[i][k]) * u) for k in range(3)))
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([px0, py0, px1, py1], radius=16 * S, fill=255)
    img.paste(grad, (0, 0), m)
    ImageDraw.Draw(img).rounded_rectangle([px0 + 2 * S, py0 + 2 * S, px1 - 2 * S, py1 - 2 * S],
                                          radius=14 * S, fill=PANEL)
    return img

BASE = base()

def frame(n1, n2, cursor):
    """n1: 1. satırda görünen harf sayısı, n2: 2. satırda; cursor: imleç görünsün mü."""
    img = BASE.copy()
    d = ImageDraw.Draw(img)
    for ch, col, f, x in C1[:n1]:
        d.text((x, Y1 * S), ch, font=f, fill=col)
    for ch, col, f, x in C2[:n2]:
        d.text((x, Y2 * S), ch, font=f, fill=col)
    if cursor:
        if n2 > 0:
            x = C2[n2 - 1][3] + C2[n2 - 1][2].getlength(C2[n2 - 1][0]) + 6 * S
            d.rectangle([x, (Y2 + 6) * S, x + 22 * S, (Y2 + 52) * S], fill=CYAN)
        else:
            x = (C1[n1 - 1][3] + C1[n1 - 1][2].getlength(C1[n1 - 1][0]) if n1 else X0 * S) + 3 * S
            d.rectangle([x, (Y1 + 2) * S, x + 11 * S, (Y1 + 28) * S], fill=CYAN)
    return img.resize((W, H), Image.LANCZOS)

frames, durs = [], []
def add(img, ms): frames.append(img); durs.append(ms)

# 1) tam görünüm (önizleme karesi), imleç yanıp söner
for k in range(10):
    add(frame(len(C1), len(C2), k % 2 == 0), 300)
# 2) temizle, komutu yaz, çıktıyı yaz
add(frame(0, 0, True), 350)
for n in range(1, len(C1) + 1):
    add(frame(n, 0, True), 55)
add(frame(len(C1), 0, True), 400)
for n in range(1, len(C2) + 1):
    add(frame(len(C1), n, True), 70)

pal = [f.convert("P", palette=Image.ADAPTIVE, colors=64, dither=Image.NONE) for f in frames]
pal[0].save("images/hello-terminal.gif", save_all=True, append_images=pal[1:],
            duration=durs, loop=0, optimize=True, disposal=1)
frames[0].save("images/_prev0.png"); frames[len(C1) + 6].save("images/_prev1.png")
print(len(frames), "kare")
