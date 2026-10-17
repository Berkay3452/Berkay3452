"""Profil banner GIF'i: beyaz kutu içinde daktilo efektli, degrade renkli, glitch geçişli metin.
Çalıştır:  python images/make_banner.py   ->  images/hello-berkay.gif
Gerekli:   pip install pillow   (Windows'ta Bahnschrift yazı tipi kullanılır)
"""
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 800, 140
S = 2                                   # süper-örnekleme (kenar yumuşatma)
BG = (13, 17, 23)
BLUE = (33, 124, 245)
FONT = "C:/Windows/Fonts/bahnschrift.ttf"
PHRASES = ["Hello Coders", "I'm Berkay Öztürk"]
SHEAR = 0.22                            # italik eğim
random.seed(7)

def font(size):
    f = ImageFont.truetype(FONT, size * S)
    try:
        f.set_variation_by_name("Bold")
    except Exception:
        pass
    return f

def make_text_layer(text, size=74):
    """Degrade renkli, italik, gölgeli metin katmanı (RGBA) ve harf başı x konumları."""
    f = font(size)
    while f.getlength(text) > (W - 150) * S and size > 20:
        size -= 2
        f = font(size)
    mask = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(mask)
    bb = d.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x0 = (W * S - tw) // 2 - bb[0]
    y0 = (H * S - th) // 2 - bb[1]
    d.text((x0, y0), text, font=f, fill=255)
    mask = mask.transform(mask.size, Image.AFFINE,
                          (1, SHEAR, -SHEAR * H * S / 2, 0, 1, 0), resample=Image.BICUBIC)
    # yatay degrade: lacivert -> mavi -> mor
    grad = Image.new("RGB", (W * S, H * S))
    gd = ImageDraw.Draw(grad)
    stops = [(10, 22, 70), (25, 105, 235), (130, 80, 223)]
    xs, xe = x0 + bb[0], x0 + bb[2]
    for x in range(W * S):
        t = min(max((x - xs) / max(xe - xs, 1), 0), 1) * 2
        i = min(int(t), 1)
        u = t - i
        c = tuple(int(stops[i][k] + (stops[i + 1][k] - stops[i][k]) * u) for k in range(3))
        gd.line([(x, 0), (x, H * S)], fill=c)
    layer = grad.convert("RGBA")
    layer.putalpha(mask)
    # mavi gölge
    sh = mask.filter(ImageFilter.GaussianBlur(3 * S))
    sh = ImageChops.offset(sh, 3 * S, 4 * S).point(lambda v: int(v * 0.45))
    shadow = Image.new("RGBA", mask.size, BLUE + (0,))
    shadow.putalpha(sh)
    # her harfin bittiği x (daktilo efekti için)
    edges = [x0 + f.getlength(text[:i + 1]) for i in range(len(text))]
    return Image.alpha_composite(shadow, layer), edges, (x0 + tw, y0, th)

def box_layer():
    """Beyaz -> açık mavi-gri degrade, yuvarlak köşeli kutu."""
    pad = 16 * S
    box = Image.new("RGB", (W * S, H * S), BG)
    g = Image.new("RGB", (W * S, H * S))
    gd = ImageDraw.Draw(g)
    for y in range(H * S):
        t = y / (H * S)
        gd.line([(0, y), (W * S, y)], fill=(int(252 - 14 * t), int(253 - 10 * t), 255))
    m = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(m).rounded_rectangle([pad, pad, W * S - pad, H * S - pad], radius=14 * S, fill=255)
    box.paste(g, (0, 0), m)
    d = ImageDraw.Draw(box)
    # mavi çerçeve çizgisi (ince)
    d.rounded_rectangle([pad, pad, W * S - pad, H * S - pad], radius=14 * S, outline=(190, 210, 245), width=S)
    return box, m

BOX, BOXMASK = box_layer()

def compose(text_layer, reveal_x=None, caret=False, sweep=None, slash_glow=0.0):
    img = BOX.copy()
    # parlama bandı (hafif mavi, çapraz)
    if sweep is not None:
        band = Image.new("L", img.size, 0)
        bd = ImageDraw.Draw(band)
        cx = int(sweep * (W + 200) * S) - 100 * S
        bd.polygon([(cx, 0), (cx + 40 * S, 0), (cx + 40 * S - 30 * S, H * S), (cx - 30 * S, H * S)], fill=70)
        band = ImageChops.multiply(band, BOXMASK)
        img.paste(Image.new("RGB", img.size, (170, 205, 255)), (0, 0), band)
    layer = text_layer
    if reveal_x is not None:
        cut = Image.new("L", img.size, 0)
        ImageDraw.Draw(cut).rectangle([0, 0, int(reveal_x + SHEAR * H * S / 2), H * S], fill=255)
        r, g, b, a = layer.split()
        layer = Image.merge("RGBA", (r, g, b, ImageChops.multiply(a, cut)))
    img.paste(layer, (0, 0), layer)
    d = ImageDraw.Draw(img)
    if caret and reveal_x is not None:
        cx = int(reveal_x + 4 * S)
        d.polygon([(cx + 10 * S, 30 * S), (cx + 15 * S, 30 * S), (cx + 5 * S, 110 * S), (cx, 110 * S)], fill=BLUE)
    # mavi köşe çizgileri (kutunun dışına taşan)
    col = tuple(int(c + (255 - c) * slash_glow * 0.5) for c in BLUE)
    lw = 5 * S
    d.line([(3 * S, 50 * S), (32 * S, 3 * S)], fill=col, width=lw)
    d.line([(W * S - 32 * S, H * S - 3 * S), (W * S - 3 * S, H * S - 50 * S)], fill=col, width=lw)
    return img

def glitch(img, strength):
    """Yatay şeritleri kaydır + kırmızı/camgöbeği kanal kayması."""
    w, h = img.size
    out = img.copy()
    y = 0
    while y < h:
        sh = random.randint(8 * S, 28 * S)
        dx = random.randint(-int(strength * 40 * S), int(strength * 40 * S))
        strip = img.crop((0, y, w, min(y + sh, h)))
        out.paste(ImageChops.offset(strip, dx, 0), (0, y))
        y += sh
    r, g, b = out.split()
    off = int(strength * 8 * S)
    r = ImageChops.offset(r, off, 0)
    b = ImageChops.offset(b, -off, 0)
    return Image.merge("RGB", (r, g, b))

def finish(img):
    return img.resize((W, H), Image.LANCZOS)

layers = [make_text_layer(t) for t in PHRASES]
frames, durs = [], []

def add(img, ms):
    frames.append(finish(img)); durs.append(ms)

def hold(i, n):
    layer, _, _ = layers[i]
    for k in range(n):
        add(compose(layer, sweep=k / (n - 1) if n > 1 else None,
                    slash_glow=0.5 + 0.5 * (k % 8 < 4)), 70)

def glitch_out(i):
    layer, _, _ = layers[i]
    base = compose(layer, slash_glow=1)
    for k, s in enumerate([0.3, 0.7, 1.0, 0.8, 0.4]):
        add(glitch(base, s), 55)
    add(compose(Image.new("RGBA", base.size, (0, 0, 0, 0)), slash_glow=1), 90)

def type_in(i):
    layer, edges, _ = layers[i]
    for n, e in enumerate(edges):
        add(compose(layer, reveal_x=e, caret=True, slash_glow=0.5), 75)
    for k in range(4):
        add(compose(layer, reveal_x=edges[-1], caret=(k % 2 == 0), slash_glow=0.5), 160)

# Sıra: ilk kare tam metin (önizleme için) -> glitch -> diğer metin yazılır -> bekler -> glitch -> ilki yazılır
hold(0, 24)
glitch_out(0)
type_in(1)
hold(1, 30)
glitch_out(1)
type_in(0)

pal = [f.convert("P", palette=Image.ADAPTIVE, colors=96, dither=Image.NONE) for f in frames]
pal[0].save("images/hello-berkay.gif", save_all=True, append_images=pal[1:],
            duration=durs, loop=0, optimize=True, disposal=1)
frames[0].save("images/preview_hello.png")
frames[len(frames) // 2 + 5].save("images/preview_name.png")
print(len(frames), "kare")
