#!/usr/bin/env python3
"""
用纯 Python (struct + zlib) 生成 DMG 背景图
尺寸: 600x380，深色主题 + 金色警告文字
"""
import struct, zlib, math, os

W, H = 600, 380

# ── 颜色 ──────────────────────────────────────────────
BG       = (18, 18, 30)       # 深蓝黑背景
GOLD     = (212, 160, 23)     # 金色
GOLD2    = (255, 200, 50)     # 高亮金
WHITE    = (255, 255, 255)
GRAY     = (160, 160, 170)
WARN_BG  = (40, 30, 10)       # 警告框背景
WARN_BOR = (160, 120, 10)     # 警告框边框

# ── 像素缓冲 ──────────────────────────────────────────
pixels = [[list(BG) for _ in range(W)] for _ in range(H)]

def setpx(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        pixels[y][x] = list(c)

def blend(base, over, a):
    return tuple(int(base[i]*(1-a) + over[i]*a) for i in range(3))

def fill_rect(x, y, w, h, c):
    for ry in range(y, y+h):
        for rx in range(x, x+w):
            setpx(rx, ry, c)

def draw_rect_border(x, y, w, h, c, thickness=1):
    for t in range(thickness):
        for rx in range(x+t, x+w-t):
            setpx(rx, y+t, c)
            setpx(rx, y+h-1-t, c)
        for ry in range(y+t, y+h-t):
            setpx(x+t, ry, c)
            setpx(x+w-1-t, ry, c)

def draw_line(x0, y0, x1, y1, c):
    dx, dy = abs(x1-x0), abs(y1-y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        setpx(x0, y0, c)
        if x0 == x1 and y0 == y1: break
        e2 = 2*err
        if e2 > -dy: err -= dy; x0 += sx
        if e2 < dx:  err += dx; y0 += sy

# ── 像素字体（5×7 点阵，ASCII 可打印字符）──────────────
FONT = {
    ' ':  [0x00,0x00,0x00,0x00,0x00],
    '!':  [0x00,0x5F,0x00,0x00,0x00],
    '#':  [0x14,0x7F,0x14,0x7F,0x14],
    '(':  [0x1C,0x22,0x41,0x00,0x00],
    ')':  [0x41,0x22,0x1C,0x00,0x00],
    '*':  [0x2A,0x1C,0x7F,0x1C,0x2A],
    '+':  [0x08,0x08,0x3E,0x08,0x08],
    ',':  [0x00,0x50,0x30,0x00,0x00],
    '-':  [0x08,0x08,0x08,0x08,0x08],
    '.':  [0x00,0x60,0x60,0x00,0x00],
    '/':  [0x20,0x10,0x08,0x04,0x02],
    '0':  [0x3E,0x51,0x49,0x45,0x3E],
    '1':  [0x00,0x42,0x7F,0x40,0x00],
    '2':  [0x42,0x61,0x51,0x49,0x46],
    '3':  [0x21,0x41,0x45,0x4B,0x31],
    '4':  [0x18,0x14,0x12,0x7F,0x10],
    '5':  [0x27,0x45,0x45,0x45,0x39],
    '6':  [0x3C,0x4A,0x49,0x49,0x30],
    '7':  [0x01,0x71,0x09,0x05,0x03],
    '8':  [0x36,0x49,0x49,0x49,0x36],
    '9':  [0x06,0x49,0x49,0x29,0x1E],
    ':':  [0x00,0x36,0x36,0x00,0x00],
    ';':  [0x00,0x56,0x36,0x00,0x00],
    '<':  [0x08,0x14,0x22,0x41,0x00],
    '=':  [0x14,0x14,0x14,0x14,0x14],
    '>':  [0x41,0x22,0x14,0x08,0x00],
    '?':  [0x02,0x01,0x51,0x09,0x06],
    '@':  [0x32,0x49,0x79,0x41,0x3E],
    'A':  [0x7E,0x11,0x11,0x11,0x7E],
    'B':  [0x7F,0x49,0x49,0x49,0x36],
    'C':  [0x3E,0x41,0x41,0x41,0x22],
    'D':  [0x7F,0x41,0x41,0x22,0x1C],
    'E':  [0x7F,0x49,0x49,0x49,0x41],
    'F':  [0x7F,0x09,0x09,0x09,0x01],
    'G':  [0x3E,0x41,0x49,0x49,0x7A],
    'H':  [0x7F,0x08,0x08,0x08,0x7F],
    'I':  [0x00,0x41,0x7F,0x41,0x00],
    'J':  [0x20,0x40,0x41,0x3F,0x01],
    'K':  [0x7F,0x08,0x14,0x22,0x41],
    'L':  [0x7F,0x40,0x40,0x40,0x40],
    'M':  [0x7F,0x02,0x0C,0x02,0x7F],
    'N':  [0x7F,0x04,0x08,0x10,0x7F],
    'O':  [0x3E,0x41,0x41,0x41,0x3E],
    'P':  [0x7F,0x09,0x09,0x09,0x06],
    'Q':  [0x3E,0x41,0x51,0x21,0x5E],
    'R':  [0x7F,0x09,0x19,0x29,0x46],
    'S':  [0x46,0x49,0x49,0x49,0x31],
    'T':  [0x01,0x01,0x7F,0x01,0x01],
    'U':  [0x3F,0x40,0x40,0x40,0x3F],
    'V':  [0x1F,0x20,0x40,0x20,0x1F],
    'W':  [0x3F,0x40,0x38,0x40,0x3F],
    'X':  [0x63,0x14,0x08,0x14,0x63],
    'Y':  [0x07,0x08,0x70,0x08,0x07],
    'Z':  [0x61,0x51,0x49,0x45,0x43],
    '[':  [0x00,0x7F,0x41,0x41,0x00],
    ']':  [0x00,0x41,0x41,0x7F,0x00],
    '_':  [0x40,0x40,0x40,0x40,0x40],
    'a':  [0x20,0x54,0x54,0x54,0x78],
    'b':  [0x7F,0x48,0x44,0x44,0x38],
    'c':  [0x38,0x44,0x44,0x44,0x20],
    'd':  [0x38,0x44,0x44,0x48,0x7F],
    'e':  [0x38,0x54,0x54,0x54,0x18],
    'f':  [0x08,0x7E,0x09,0x01,0x02],
    'g':  [0x0C,0x52,0x52,0x52,0x3E],
    'h':  [0x7F,0x08,0x04,0x04,0x78],
    'i':  [0x00,0x44,0x7D,0x40,0x00],
    'j':  [0x20,0x40,0x44,0x3D,0x00],
    'k':  [0x7F,0x10,0x28,0x44,0x00],
    'l':  [0x00,0x41,0x7F,0x40,0x00],
    'm':  [0x7C,0x04,0x18,0x04,0x78],
    'n':  [0x7C,0x08,0x04,0x04,0x78],
    'o':  [0x38,0x44,0x44,0x44,0x38],
    'p':  [0x7C,0x14,0x14,0x14,0x08],
    'q':  [0x08,0x14,0x14,0x18,0x7C],
    'r':  [0x7C,0x08,0x04,0x04,0x08],
    's':  [0x48,0x54,0x54,0x54,0x20],
    't':  [0x04,0x3F,0x44,0x40,0x20],
    'u':  [0x3C,0x40,0x40,0x20,0x7C],
    'v':  [0x1C,0x20,0x40,0x20,0x1C],
    'w':  [0x3C,0x40,0x30,0x40,0x3C],
    'x':  [0x44,0x28,0x10,0x28,0x44],
    'y':  [0x0C,0x50,0x50,0x50,0x3C],
    'z':  [0x44,0x64,0x54,0x4C,0x44],
}

def draw_char(cx, cy, ch, color, scale=1):
    bits = FONT.get(ch, FONT.get(' '))
    for col, byte in enumerate(bits):
        for row in range(7):
            if byte & (1 << row):
                for sy in range(scale):
                    for sx in range(scale):
                        setpx(cx + col*scale + sx, cy + row*scale + sy, color)
    return cx + (len(bits)+1) * scale

def draw_text(x, y, text, color, scale=1):
    cx = x
    for ch in text:
        if ch in FONT:
            cx = draw_char(cx, y, ch, color, scale)
        else:
            cx += 6 * scale
    return cx

# ── 绘制渐变背景 ─────────────────────────────────────
for ry in range(H):
    t = ry / H
    c = (int(18 + 10*t), int(18 + 8*t), int(30 + 15*t))
    for rx in range(W):
        pixels[ry][rx] = list(c)

# 顶部金色分割线
for rx in range(W):
    setpx(rx, 0, GOLD)
    setpx(rx, 1, GOLD)

# 底部金色分割线
for rx in range(W):
    setpx(rx, H-2, GOLD)
    setpx(rx, H-1, GOLD)

# ── 顶部标题区 ──────────────────────────────────────
# 标题背景
for ry in range(2, 42):
    t = (ry-2)/40
    c = (int(25+10*t), int(20+10*t), int(10+5*t))
    for rx in range(W):
        pixels[ry][rx] = list(c)

# "Gold Price Float" 英文标题（放大 2x）
title = "Gold Price  Float  Window"
tx = draw_text(20, 12, title, GOLD2, scale=2)

# 金色装饰线（标题下方）
for rx in range(W):
    c_t = rx / W
    c = (int(GOLD[0]*c_t + GOLD2[0]*(1-c_t)),
         int(GOLD[1]*c_t + GOLD2[1]*(1-c_t)),
         int(GOLD[2]*c_t + GOLD2[2]*(1-c_t)))
    setpx(rx, 42, c)
    setpx(rx, 43, c)

# ── 中间区域：图标占位 + 箭头 + Applications ────────
# 应用图标圆形占位（左侧）
cx_app, cy_app = 150, 155
for ry in range(cy_app-50, cy_app+50):
    for rx in range(cx_app-50, cx_app+50):
        dist = math.sqrt((rx-cx_app)**2 + (ry-cy_app)**2)
        if dist < 48:
            t = 1 - dist/48
            c = blend(BG, GOLD, t*0.3)
            setpx(rx, ry, c)
        if 46 <= dist < 50:
            setpx(rx, ry, GOLD)

# 应用图标里画小"金"字形状（简单方块组合）
for ry in range(cy_app-20, cy_app+20):
    for rx in range(cx_app-20, cx_app+20):
        setpx(rx, ry, GOLD)
for ry in range(cy_app-18, cy_app+18):
    for rx in range(cx_app-18, cx_app+18):
        setpx(rx, ry, (30, 25, 5))
# 画 ¥ 符号轮廓
for rx in range(cx_app-12, cx_app+12):
    setpx(rx, cy_app-5, GOLD2)
    setpx(rx, cy_app+2, GOLD2)
for ry in range(cy_app+2, cy_app+14):
    setpx(cx_app, ry, GOLD2)
    setpx(cx_app-1, ry, GOLD2)
for rx, ry in [(-12,cy_app-16),(-8,cy_app-10),(0,cy_app-2),(8,cy_app-10),(12,cy_app-16)]:
    for dy in range(-1,2):
        for dx in range(-1,2):
            setpx(cx_app+rx+dx, ry+dy, GOLD2)

# 应用名称（图标下方）
app_label = "Jin Jia  FuDong Chuang"
lw = len([c for c in app_label if c in FONT]) * 6 + (len(app_label)-len([c for c in app_label if c in FONT]))*6
draw_text(cx_app - 55, cy_app + 58, app_label, GOLD, scale=1)

# 箭头（中间）
ax, ay = 300, 150
for rx in range(ax-20, ax+20):
    setpx(rx, ay, GOLD2)
    setpx(rx, ay+1, GOLD2)
for dy in range(-10, 11):
    setpx(ax+10+abs(dy)//1, ay+dy, GOLD2)
for dy in range(-12, 13):
    ax2 = ax + 10
    if dy == 0: continue
    sign = 1 if dy > 0 else -1
    for t in range(abs(dy)):
        setpx(ax2 + t, ay + sign*t//1, GOLD2)

# 重画简单箭头
for rx in range(ax-25, ax+15):
    setpx(rx, ay, GOLD2)
    setpx(rx, ay+2, GOLD2)
    setpx(rx, ay+1, GOLD2)
for i in range(15):
    setpx(ax+15-i, ay-i, GOLD2)
    setpx(ax+15-i, ay+2+i, GOLD2)
    setpx(ax+15, ay-i, GOLD2)
    setpx(ax+15, ay+2+i, GOLD2)

# Applications 文件夹图标（右侧）
cx_dst, cy_dst = 450, 155
# 文件夹形状
fill_rect(cx_dst-40, cy_dst-25, 80, 55, (50, 80, 130))
fill_rect(cx_dst-40, cy_dst-35, 35, 12, (50, 80, 130))
draw_rect_border(cx_dst-40, cy_dst-35, 35, 12, (80, 120, 180), 2)
draw_rect_border(cx_dst-40, cy_dst-25, 80, 55, (80, 120, 180), 2)
# 文件夹里写 A
draw_text(cx_dst-5, cy_dst-10, "App", WHITE, scale=1)
draw_text(cx_dst-8, cy_dst+5, "licatn", WHITE, scale=1)

draw_text(cx_dst-27, cy_dst+58, "Applications", WHITE, scale=1)

# ── 警告信息框 ──────────────────────────────────────
box_x, box_y, box_w, box_h = 20, 225, 560, 140
# 警告框背景（半透明深橙）
for ry in range(box_y, box_y+box_h):
    for rx in range(box_x, box_x+box_w):
        pixels[ry][rx] = list(blend(tuple(pixels[ry][rx]), WARN_BG, 0.85))

draw_rect_border(box_x, box_y, box_w, box_h, WARN_BOR, 2)

# 警告图标 ⚠  (三角形)
tx_warn, ty_warn = box_x + 18, box_y + 14
tri_pts = [(tx_warn, ty_warn+24), (tx_warn+14, ty_warn), (tx_warn+28, ty_warn+24)]
# 画三角形边
for i in range(3):
    x0,y0 = tri_pts[i]
    x1,y1 = tri_pts[(i+1)%3]
    draw_line(x0,y0,x1,y1, GOLD2)
# 感叹号
for ry in range(ty_warn+8, ty_warn+18):
    setpx(tx_warn+14, ry, GOLD2)
    setpx(tx_warn+13, ry, GOLD2)
setpx(tx_warn+14, ty_warn+21, GOLD2)
setpx(tx_warn+13, ty_warn+21, GOLD2)

# 警告标题（ASCII）
draw_text(box_x+55, box_y+10, "NOTICE:  First  Launch  on  macOS", GOLD2, scale=2)

# 分割线
for rx in range(box_x+10, box_x+box_w-10):
    setpx(rx, box_y+36, WARN_BOR)

# 警告内容行（英文，因为只有ASCII字体）
lines = [
    ("1. macOS may say [unidentified developer] - this is normal", WHITE),
    ("2. Right-click the app -> click [Open] in the menu", WHITE),
    ("3. Click [Open] in the popup dialog to confirm", WHITE),
    ("4. After that, you can double-click to launch normally", GRAY),
]
for i, (line, color) in enumerate(lines):
    draw_text(box_x+20, box_y+44+i*22, line, color, scale=1)

# ── 底部版本信息 ─────────────────────────────────────
draw_text(W//2-60, H-18, "v0.1.0  -  Gold  Price  Float  Window", GRAY, scale=1)

# ── 生成 PNG ──────────────────────────────────────────
def make_png(pixels, w, h):
    def chunk(tag, data):
        c = zlib.crc32(tag + data) & 0xffffffff
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', c)

    raw = b''
    for row in pixels:
        raw += b'\x00'
        for px in row:
            raw += bytes(px)

    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    idat = zlib.compress(raw, 9)
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', idat)
            + chunk(b'IEND', b''))

out_path = os.path.join(os.path.dirname(__file__), 'dmg_background.png')
with open(out_path, 'wb') as f:
    f.write(make_png(pixels, W, H))
print(f"✅ DMG 背景图已生成: {out_path}  ({W}x{H}px)")
