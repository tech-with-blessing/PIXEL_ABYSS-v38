"""
PIXEL ABYSS — Level Viewer (pygame)
Works on PC and mobile/touch screens.

PC controls:
  Mouse drag        — pan canvas
  Scroll wheel      — zoom
  F                 — fit to level
  1-9               — toggle layers
  Arrow keys        — pan
  +/-               — zoom
  ESC               — back to level list

Mobile / touch controls:
  1-finger drag     — pan canvas
  2-finger pinch    — zoom
  Tap layer row     — toggle layer
  Tap buttons       — Fit / Back / zoom +/-
"""

import pygame
import json
import os
import sys
import math
import re

# ── Try to import block palette ────────────────────────────────────────────────
try:
    from game.data.palletes.blocks import block_pallete as BLOCK_PALETTE
except ImportError:
    BLOCK_PALETTE = {}

# ── Colours ────────────────────────────────────────────────────────────────────
BG       = (7,   8,  15)
SURFACE  = (14,  16,  32)
ACCENT   = (61, 107, 255)
ACCENT2  = (255, 68, 102)
TEXT     = (200, 208, 240)
MUTED    = (90,  96, 128)
BORDER   = (30,  45, 100)
GOLD     = (255, 215,   0)
BTN_BG   = (22,  28,  60)
BTN_HOV  = (40,  60, 130)

# ── Fallback palette colours ───────────────────────────────────────────────────
PAL_STONE = {'': (90,106,106),'2':(58,42,90),'3':(138,112,64),
             '4':(58,90,48),'5':(96,120,150),'6':(106,32,32),'7':(42,26,74),'8':(138,85,32)}
PAL_GRASS = {'': (58,122,58),'2':(74,58,106),'3':(154,128,80),
             '4':(74,106,56),'5':(112,138,170),'6':(122,40,40),'7':(58,42,90),'8':(154,101,48)}
PAL_BRICK = {'': (138,64,48),'2':(90,48,96),'3':(160,120,72),
             '4':(80,122,72),'5':(112,138,170),'6':(138,40,40),'7':(58,40,88),'8':(160,112,64)}

ENEMY_CLR    = {'Red':(224,64,64),'Blue':(64,112,224),'Yellow':(212,192,48),'Purple':(144,64,192)}
TREASURE_CLR = {'red':(224,64,48),'pink':(224,112,160),'green':(64,192,64),'yellow':(216,192,48)}
PAL_NAMES    = {1:'Default',2:'Purple',3:'Sandy',4:'Mossy',5:'Snow',6:'Nether',7:'Void',8:'Autumn'}

# ── Palette colour extraction from blocks.py ───────────────────────────────────
def _palette_base_colour(block_type, suffix):
    pal_str = str(suffix) if suffix else '1'
    data = BLOCK_PALETTE.get(block_type, {}).get(pal_str, [])
    if data:
        return tuple(data[0][1])   # first entry's accent colour
    return None


def _pal(paldict, suffix):
    return paldict.get(suffix, paldict.get('', (90, 106, 106)))


def block_color(name):
    m = re.search(r'_(\d)$', name)
    p = m.group(1) if m else ''
    if name.startswith('grass'):
        c = _palette_base_colour('grass', p if p else '1')
        return c if c else _pal(PAL_GRASS, p)
    if name.startswith('stone'):
        c = _palette_base_colour('stone', p if p else '1')
        return c if c else _pal(PAL_STONE, p)
    if name.startswith('brick'):
        c = _palette_base_colour('brick', p if p else '1')
        return c if c else _pal(PAL_BRICK, p)
    if name.startswith('sand'):   return (200, 168,  64)
    if name.startswith('mud'):    return (106,  72,  32)
    if name.startswith('ice'):    return (160, 200, 224)
    if name.startswith('box'):    return (200, 168,  80)
    if name.startswith('window'): return ( 96, 144, 200)
    return (90, 106, 106)


def get_color(obj):
    t = obj.get('type', '')
    if t == 'start':   return (255, 255, 255)
    if t == 'block':
        if obj.get('perspective') == 'back': return None
        return block_color(obj.get('name', ''))
    if t == 'enemy':          return ENEMY_CLR.get(obj.get('color',''), (224,64,64))
    if t == 'spawn_point':    return (255, 136, 0)
    if t == 'tree':           return (34, 136, 51)
    if t == 'deco':           return (160, 80, 0)
    if t == 'treasure':       return TREASURE_CLR.get(obj.get('name',''), GOLD)
    if t == 'water':
        c = obj.get('color'); return tuple(c) if c else (34, 85, 204)
    if t == 'moving_platform':
        c = obj.get('color'); return tuple(c) if c else (85, 136, 255)
    return (136, 136, 136)

# ── Layer config ───────────────────────────────────────────────────────────────
LAYERS = [
    ('block',    'Fore blocks',  (74, 122,  80)),
    ('back',     'Back blocks',  (42,  58,  94)),
    ('water',    'Water/lava',   (34,  85, 204)),
    ('tree',     'Trees',        (34, 136,  51)),
    ('deco',     'Decos',       (160,  80,   0)),
    ('treasure', 'Treasure',     GOLD),
    ('enemy',    'Enemies',     (224,  64,  64)),
    ('spawn',    'Spawn pts',   (255, 136,   0)),
    ('platform', 'Platforms',   ( 85, 136, 255)),
]
LAYER_KEYS = [getattr(pygame, f'K_{i}') for i in range(1, 10)]
DRAW_ORDER = ['water','back','block','deco','tree','treasure','platform','spawn','enemy','start']

# ── Viewport ───────────────────────────────────────────────────────────────────
class Viewport:
    def __init__(self):
        self.ox = 0.0
        self.oy = 0.0
        self.scale = 0.09

    def w2s(self, wx, wy):
        return wx * self.scale + self.ox, wy * self.scale + self.oy

    def s2w(self, sx, sy):
        return (sx - self.ox) / self.scale, (sy - self.oy) / self.scale

    def zoom(self, factor, cx, cy):
        self.ox = cx + (self.ox - cx) * factor
        self.oy = cy + (self.oy - cy) * factor
        self.scale = max(0.005, min(self.scale * factor, 8.0))

    def fit(self, objects, canvas_x, canvas_y, canvas_w, canvas_h):
        mn_x = mn_y =  math.inf
        mx_x = mx_y = -math.inf
        for o in objects:
            if o.get('type') == 'entity settings': continue
            x, y = o.get('x', 0), o.get('y', 0)
            w, h = o.get('width', 64), o.get('height', 64)
            mn_x = min(mn_x, x);  mx_x = max(mx_x, x+w)
            mn_y = min(mn_y, y);  mx_y = max(mx_y, y+h)
        if not math.isfinite(mn_x): return
        dw, dh = mx_x-mn_x, mx_y-mn_y
        pad = 40
        sx = (canvas_w - pad*2) / dw if dw else 1
        sy = (canvas_h - pad*2) / dh if dh else 1
        self.scale = max(0.005, min(min(sx, sy), 2.0))
        self.ox = canvas_x + canvas_w/2 - (mn_x + dw/2) * self.scale
        self.oy = canvas_y + canvas_h/2 - (mn_y + dh/2) * self.scale

# ── Drawing helpers ────────────────────────────────────────────────────────────
def draw_circle(surf, colour, cx, cy, r, alpha=255, border=None, border_col=None):
    if r < 1: return
    s = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
    pygame.draw.circle(s, (*colour, alpha), (r+1, r+1), r)
    if border and border_col:
        pygame.draw.circle(s, (*border_col, 200), (r+1, r+1), r, max(1, int(border)))
    surf.blit(s, (int(cx-r-1), int(cy-r-1)))


def draw_rect_alpha(surf, colour, rect, alpha):
    s = pygame.Surface((max(1,int(rect[2])), max(1,int(rect[3]))), pygame.SRCALPHA)
    s.fill((*colour, alpha))
    surf.blit(s, (int(rect[0]), int(rect[1])))


def draw_panel(surf, rect, alpha=220, colour=None):
    c = colour or SURFACE
    s = pygame.Surface((max(1,int(rect[2])), max(1,int(rect[3]))), pygame.SRCALPHA)
    s.fill((*c, alpha))
    surf.blit(s, (int(rect[0]), int(rect[1])))
    pygame.draw.rect(surf, BORDER, (int(rect[0]),int(rect[1]),int(rect[2]),int(rect[3])), 1)


def draw_text(surf, font, text, colour, x, y):
    t = font.render(str(text), True, colour)
    surf.blit(t, (int(x), int(y)))
    return t.get_width(), t.get_height()


def draw_button(surf, font, label, rect, hovered=False):
    bg  = BTN_HOV if hovered else BTN_BG
    draw_panel(surf, rect, alpha=230, colour=bg)
    pygame.draw.rect(surf, ACCENT, (int(rect[0]),int(rect[1]),int(rect[2]),int(rect[3])), 1)
    tw, th = font.size(label)
    draw_text(surf, font, label, TEXT,
              rect[0] + (rect[2]-tw)//2,
              rect[1] + (rect[3]-th)//2)


def draw_object(surf, obj, vp, font_tiny):
    sx, sy = vp.w2s(obj.get('x',0), obj.get('y',0))
    sw = max(obj.get('width', 64)  * vp.scale, 1.5)
    sh = max(obj.get('height', 64) * vp.scale, 1.5)
    t  = obj.get('type', '')

    if t == 'water':
        c = get_color(obj)
        draw_rect_alpha(surf, c, (sx,sy,sw,sh), 140)
        if obj.get('rise'):
            pygame.draw.rect(surf, (200,200,255), (int(sx),int(sy),max(1,int(sw)),max(1,int(sh))), 1)

    elif t == 'block' and obj.get('perspective') == 'back':
        c = block_color(obj.get('name',''))
        draw_rect_alpha(surf, c, (sx,sy,sw,sh), 90)
        pygame.draw.rect(surf, (80,120,200), (int(sx),int(sy),max(1,int(sw)),max(1,int(sh))), 1)

    elif t == 'block':
        c = get_color(obj)
        pygame.draw.rect(surf, c, (int(sx),int(sy),max(1,int(sw)),max(1,int(sh))))
        if sw > 3:
            pygame.draw.rect(surf, (0,0,0), (int(sx),int(sy),max(1,int(sw)),max(1,int(sh))), 1)

    elif t == 'start':
        r = max(sw/2, 3)
        draw_circle(surf,(255,255,255), sx+sw/2, sy+sh/2, int(r), border=1.5, border_col=(255,255,0))
        if r > 4:
            draw_circle(surf,(255,255,0), sx+sw/2, sy+sh/2, max(1,int(r*0.35)))

    elif t == 'enemy':
        c = get_color(obj)
        r = max(sw/2, 3)
        draw_circle(surf, c, sx+sw/2, sy+sh/2, int(r), border=0.7, border_col=(255,255,255))
        if r > 5:
            draw_circle(surf,(255,255,255), sx+sw/2, sy+sh/2, max(1,int(r*0.3)), alpha=150)
        if r > 8 and obj.get('name'):
            lbl = font_tiny.render(obj['name'][:6], True, (255,255,255))
            surf.blit(lbl,(int(sx+sw/2-lbl.get_width()/2), int(sy+sh/2+r+1)))

    elif t == 'spawn_point':
        draw_rect_alpha(surf,(255,136,0),(sx,sy,sw,sh),165)
        pygame.draw.rect(surf,(255,170,0),(int(sx),int(sy),max(1,int(sw)),max(1,int(sh))),1)

    elif t == 'tree':
        r = max(sw/2, 3)
        draw_circle(surf,(34,136,51), sx+sw/2, sy+sh/2, int(r))
        if r > 5:
            draw_circle(surf,(26,102,40), sx+sw/2+r*0.22, sy+sh/2-r*0.22, max(1,int(r*0.58)))

    elif t == 'deco':
        s2 = max(sw*0.72, 2)
        draw_rect_alpha(surf,(160,80,0),(sx+sw/2-s2/2, sy+sh/2-s2/2, s2, s2),217)

    elif t == 'treasure':
        c  = get_color(obj)
        ts = max(sw*0.82, 3)
        pygame.draw.rect(surf, c,(int(sx+sw/2-ts/2),int(sy+sh/2-ts/2),max(1,int(ts)),max(1,int(ts))))
        pygame.draw.rect(surf,(255,255,255),(int(sx+sw/2-ts/2),int(sy+sh/2-ts/2),max(1,int(ts)),max(1,int(ts))),1)
        if ts > 6:
            hs = max(1,int(ts*0.38))
            s = pygame.Surface((hs,hs),pygame.SRCALPHA); s.fill((255,255,255,127))
            surf.blit(s,(int(sx+sw/2-ts/2+1),int(sy+sh/2-ts/2+1)))

    elif t == 'moving_platform':
        c = get_color(obj)
        draw_rect_alpha(surf, c,(sx,sy,max(sw,4),max(sh,2)),217)
        dx_list = obj.get('dest_x',[])
        if dx_list and len(dx_list) >= 2:
            rx0,_ = vp.w2s(dx_list[0], obj.get('y',0))
            rx1,_ = vp.w2s(dx_list[1], obj.get('y',0))
            if rx1 > rx0:
                s2 = pygame.Surface((max(1,int(rx1-rx0)),max(1,int(sh)+2)),pygame.SRCALPHA)
                pygame.draw.rect(s2,(80,130,255,64),(0,0,max(1,int(rx1-rx0)),max(1,int(sh)+2)),1)
                surf.blit(s2,(int(rx0),int(sy)))

# ── Touch state ────────────────────────────────────────────────────────────────
class TouchState:
    def __init__(self):
        self.fingers = {}

    def update(self, fid, x, y): self.fingers[fid] = (x, y)
    def remove(self, fid):       self.fingers.pop(fid, None)
    def count(self):             return len(self.fingers)

    def centroid(self):
        pts = list(self.fingers.values())
        if not pts: return (0, 0)
        return (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))

    def span(self):
        pts = list(self.fingers.values())
        if len(pts) < 2: return 0
        return math.hypot(pts[0][0]-pts[1][0], pts[0][1]-pts[1][1])

# ── Level list ─────────────────────────────────────────────────────────────────
def list_levels(levels_dir):
    if not os.path.isdir(levels_dir): return []
    return sorted(f for f in os.listdir(levels_dir) if f.endswith('.json'))


def run_level_list(screen, clock, fonts, levels_dir):
    font_lg, font_md, font_sm, font_tiny = fonts
    selected   = 0
    scroll     = 0
    levels     = list_levels(levels_dir)
    search     = ''
    searching  = False
    touch      = TouchState()
    last_ty    = None
    tap_start  = None
    last_tap_i = -1
    last_tap_t = 0

    while True:
        W, H     = screen.get_size()
        query    = search.lower().strip()
        filtered = [l for l in levels if query in l.lower()] if query else levels[:]
        ITEM_H   = max(44, H // 15)
        START_Y  = 118

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return None

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if searching: searching=False; search=''
                    else: return None
                elif ev.key == pygame.K_RETURN and filtered:
                    return os.path.join(levels_dir, filtered[min(selected,len(filtered)-1)])
                elif ev.key == pygame.K_DOWN: selected = min(selected+1,max(0,len(filtered)-1))
                elif ev.key == pygame.K_UP:   selected = max(selected-1,0)
                elif ev.key == pygame.K_BACKSPACE: search=search[:-1]; selected=0
                elif ev.key == pygame.K_SLASH: searching=True
                elif searching and ev.unicode.isprintable(): search+=ev.unicode; selected=0

            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx,my = ev.pos
                if ev.button in (4,5): scroll += -3 if ev.button==4 else 3
                elif ev.button == 1:
                    if START_Y-6 <= my <= START_Y+6+36: searching=True
                    else:
                        idx=(my-START_Y)//ITEM_H+scroll
                        if 0<=idx<len(filtered):
                            now=pygame.time.get_ticks()
                            if idx==last_tap_i and now-last_tap_t<400:
                                return os.path.join(levels_dir,filtered[idx])
                            last_tap_i=idx; last_tap_t=now; selected=idx

            if ev.type == pygame.FINGERDOWN:
                fx,fy=int(ev.x*W),int(ev.y*H)
                touch.update(ev.finger_id,fx,fy)
                last_ty=fy; tap_start=(fx,fy,pygame.time.get_ticks())

            if ev.type == pygame.FINGERMOTION:
                fx,fy=int(ev.x*W),int(ev.y*H)
                if last_ty is not None and touch.count()==1:
                    scroll-=(fy-last_ty)//max(1,ITEM_H//2)
                last_ty=fy; touch.update(ev.finger_id,fx,fy)
                if tap_start and math.hypot(fx-tap_start[0],fy-tap_start[1])>14: tap_start=None

            if ev.type == pygame.FINGERUP:
                fx,fy=int(ev.x*W),int(ev.y*H)
                if tap_start:
                    dist=math.hypot(fx-tap_start[0],fy-tap_start[1])
                    dt=pygame.time.get_ticks()-tap_start[2]
                    if dist<20 and dt<300:
                        tx,ty=tap_start[:2]
                        if ty<START_Y: searching=True
                        else:
                            idx=(ty-START_Y)//ITEM_H+scroll
                            if 0<=idx<len(filtered):
                                now=pygame.time.get_ticks()
                                if idx==last_tap_i and now-last_tap_t<500:
                                    touch.remove(ev.finger_id)
                                    return os.path.join(levels_dir,filtered[idx])
                                last_tap_i=idx; last_tap_t=now; selected=idx
                tap_start=None; last_ty=None; touch.remove(ev.finger_id)

        vis_rows   = max(1,(H-START_Y-50)//ITEM_H)
        max_scroll = max(0,len(filtered)-vis_rows)
        scroll=max(0,min(scroll,max_scroll))
        if selected<scroll: scroll=selected
        if selected>=scroll+vis_rows: scroll=selected-vis_rows+1

        screen.fill(BG)
        draw_panel(screen,(0,0,W,62))
        tw,_=draw_text(screen,font_lg,'PIXEL',TEXT,16,10)
        draw_text(screen,font_lg,'ABYSS',ACCENT,16+tw,10)
        draw_text(screen,font_sm,'LEVEL VIEWER',MUTED,16,42)
        draw_text(screen,font_sm,f'levels/  {len(levels)} files',MUTED,W-170,20)

        # Search bar
        draw_panel(screen,(10,68,W-20,38))
        pygame.draw.rect(screen,ACCENT if searching else BORDER,(10,68,W-20,38),1)
        prefix='Search: ' if searching else 'Tap to search…'
        draw_text(screen,font_sm,prefix+search+('|' if searching else ''),
                  TEXT if searching else MUTED,20,80)

        # Items
        for i,fname in enumerate(filtered):
            iy=START_Y+(i-scroll)*ITEM_H
            if iy<START_Y-ITEM_H or iy>H: continue
            is_sel=(i==selected)
            r=(10,iy,W-20,ITEM_H-3)
            if is_sel:
                draw_rect_alpha(screen,ACCENT,r,45)
                pygame.draw.rect(screen,ACCENT,(int(r[0]),int(r[1]),int(r[2]),int(r[3])),1)
            else:
                pygame.draw.rect(screen,BORDER,(int(r[0]),int(r[1]),int(r[2]),int(r[3])),1)
            name=fname[:-5] if fname.endswith('.json') else fname
            draw_text(screen,font_md,name,TEXT if is_sel else MUTED,22,iy+(ITEM_H-font_md.get_height())//2)

        if not filtered:
            msg='No levels found in levels/' if not search else f'No match for "{search}"'
            tw2,_=font_sm.size(msg)
            draw_text(screen,font_sm,msg,MUTED,(W-tw2)//2,H//2)

        draw_panel(screen,(0,H-34,W,34))
        draw_text(screen,font_tiny,'↑↓  navigate    ENTER / double-tap  load    ESC  quit',MUTED,12,H-22)

        pygame.display.flip()
        clock.tick(60)

# ── Main viewer ────────────────────────────────────────────────────────────────
def run_viewer(screen, clock, fonts, filepath):
    font_lg, font_md, font_sm, font_tiny = fonts

    try:
        with open(filepath,'r',encoding='utf-8') as f:
            data=json.load(f)
    except Exception as e:
        return f'Error: {e}'
    if not isinstance(data,list): return 'Expected a JSON array'

    objects  = data
    filename = os.path.basename(filepath)

    SIDEBAR_W = 224
    DRAWER_H  = 264

    def get_layout(W,H):
        mobile = W < 680
        if mobile:
            return mobile,(0,0,W,H-DRAWER_H),(0,H-DRAWER_H,W,DRAWER_H)
        return mobile,(SIDEBAR_W,0,W-SIDEBAR_W,H),(0,0,SIDEBAR_W,H)

    W,H = screen.get_size()
    mobile,canvas_rect,sidebar_rect = get_layout(W,H)
    cx,cy,cw,ch = canvas_rect

    vp = Viewport()
    vp.fit(objects,cx,cy,cw,ch)

    layer_vis   = {k:True for k,_,_ in LAYERS}
    layer_rects = {}

    def compute_stats():
        counts={k:0 for k,_,_ in LAYERS}; total=0; palettes=set()
        for o in objects:
            if o.get('type')=='entity settings': continue
            total+=1; t=o.get('type','')
            if t=='block':
                key='back' if o.get('perspective')=='back' else 'block'
                counts[key]=counts.get(key,0)+1
                m=re.search(r'_(\d)$',o.get('name',''))
                if m: palettes.add(int(m.group(1)))
            elif t=='spawn_point':     counts['spawn']=counts.get('spawn',0)+1
            elif t=='moving_platform': counts['platform']=counts.get('platform',0)+1
            elif t in counts: counts[t]+=1
        return total,counts,palettes

    total,counts,palettes=compute_stats()

    def is_visible(obj):
        t=obj.get('type','')
        if t=='entity settings': return False
        if t=='start': return True
        if t=='block': return layer_vis['back'] if obj.get('perspective')=='back' else layer_vis['block']
        if t=='enemy': return layer_vis['enemy']
        if t=='spawn_point': return layer_vis['spawn']
        if t=='tree': return layer_vis['tree']
        if t=='deco': return layer_vis['deco']
        if t=='treasure': return layer_vis['treasure']
        if t=='water': return layer_vis['water']
        if t=='moving_platform': return layer_vis['platform']
        return True

    def hit_test(px,py):
        for obj in reversed(objects):
            if not is_visible(obj) or obj.get('type')=='entity settings': continue
            ox,oy=vp.w2s(obj.get('x',0),obj.get('y',0))
            sw=max(obj.get('width',64)*vp.scale,4)
            sh=max(obj.get('height',64)*vp.scale,4)
            if ox<=px<=ox+sw and oy<=py<=oy+sh: return obj
        return None

    def in_canvas(px,py): return cx<=px<cx+cw and cy<=py<cy+ch

    # Input state
    dragging=False; drag_last=(0,0)
    tooltip_obj=None; tap_obj=None
    mouse_pos=(0,0)
    touch=TouchState()
    prev_centroid=None; prev_span=None
    tap_start=None; tap_start_t=0

    while True:
        W,H=screen.get_size()
        mobile,canvas_rect,sidebar_rect=get_layout(W,H)
        cx,cy,cw,ch=canvas_rect
        sx0,sy0,sw0,sh0=sidebar_rect
        mx,my=mouse_pos

        # On-screen buttons — always visible in canvas corners
        BTN_H=max(34,min(46,ch//14))
        BTN_W=max(52,min(70,cw//9))
        bpad=6
        # Top-right: Fit, Z+, Z-
        btn_fit  = pygame.Rect(cx+cw-BTN_W-bpad,      cy+bpad,               BTN_W,BTN_H)
        btn_zi   = pygame.Rect(cx+cw-BTN_W-bpad,      cy+bpad+(BTN_H+bpad),  BTN_W,BTN_H)
        btn_zo   = pygame.Rect(cx+cw-BTN_W-bpad,      cy+bpad+(BTN_H+bpad)*2,BTN_W,BTN_H)
        # Top-left: Back
        btn_back = pygame.Rect(cx+bpad,               cy+bpad,               BTN_W,BTN_H)

        def bhov(r): return pygame.Rect(r).collidepoint(mx,my)

        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: return 'quit'

            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE: return 'back'
                if ev.key==pygame.K_f: vp.fit(objects,cx,cy,cw,ch)
                for i,(k,_,_) in enumerate(LAYERS):
                    if i<len(LAYER_KEYS) and ev.key==LAYER_KEYS[i]:
                        layer_vis[k]=not layer_vis[k]
                step=max(20,cw//10)
                if ev.key==pygame.K_LEFT:  vp.ox+=step
                if ev.key==pygame.K_RIGHT: vp.ox-=step
                if ev.key==pygame.K_UP:    vp.oy+=step
                if ev.key==pygame.K_DOWN:  vp.oy-=step
                if ev.key in(pygame.K_PLUS,pygame.K_EQUALS,pygame.K_KP_PLUS):
                    vp.zoom(1.3,cx+cw/2,cy+ch/2)
                if ev.key in(pygame.K_MINUS,pygame.K_KP_MINUS):
                    vp.zoom(0.77,cx+cw/2,cy+ch/2)

            if ev.type==pygame.MOUSEMOTION:
                mouse_pos=ev.pos; mx,my=ev.pos
                if dragging:
                    vp.ox+=ev.pos[0]-drag_last[0]
                    vp.oy+=ev.pos[1]-drag_last[1]
                    drag_last=ev.pos

            if ev.type==pygame.MOUSEBUTTONDOWN:
                mx,my=ev.pos; mouse_pos=(mx,my)
                if ev.button==4: vp.zoom(1.15,mx,my)
                if ev.button==5: vp.zoom(0.87,mx,my)
                if ev.button==1:
                    if btn_fit.collidepoint(mx,my):  vp.fit(objects,cx,cy,cw,ch)
                    elif btn_zi.collidepoint(mx,my): vp.zoom(1.3,cx+cw/2,cy+ch/2)
                    elif btn_zo.collidepoint(mx,my): vp.zoom(0.77,cx+cw/2,cy+ch/2)
                    elif btn_back.collidepoint(mx,my): return 'back'
                    else:
                        # Layer toggle via sidebar row rects
                        toggled=False
                        for k,r in layer_rects.items():
                            if pygame.Rect(r).collidepoint(mx,my):
                                layer_vis[k]=not layer_vis[k]; toggled=True; break
                        if not toggled and in_canvas(mx,my):
                            dragging=True; drag_last=(mx,my)

            if ev.type==pygame.MOUSEBUTTONUP:
                if ev.button==1: dragging=False

            # Touch
            if ev.type==pygame.FINGERDOWN:
                fx,fy=int(ev.x*W),int(ev.y*H)
                touch.update(ev.finger_id,fx,fy)
                if touch.count()==1:
                    prev_centroid=(fx,fy); prev_span=None
                    tap_start=(fx,fy); tap_start_t=pygame.time.get_ticks()
                elif touch.count()==2:
                    prev_span=touch.span()
                    prev_centroid=touch.centroid()
                    tap_start=None

            if ev.type==pygame.FINGERMOTION:
                fx,fy=int(ev.x*W),int(ev.y*H)
                touch.update(ev.finger_id,fx,fy)
                if touch.count()==1 and prev_centroid:
                    nc=touch.centroid()
                    if in_canvas(int(nc[0]),int(nc[1])):
                        vp.ox+=nc[0]-prev_centroid[0]
                        vp.oy+=nc[1]-prev_centroid[1]
                    prev_centroid=nc
                    if tap_start and math.hypot(fx-tap_start[0],fy-tap_start[1])>14:
                        tap_start=None
                elif touch.count()==2 and prev_centroid:
                    nc=touch.centroid()
                    ns=touch.span()
                    if prev_span and prev_span>0:
                        vp.ox+=nc[0]-prev_centroid[0]
                        vp.oy+=nc[1]-prev_centroid[1]
                        vp.zoom(ns/prev_span,nc[0],nc[1])
                    prev_centroid=nc; prev_span=ns

            if ev.type==pygame.FINGERUP:
                fx,fy=int(ev.x*W),int(ev.y*H)
                dt=pygame.time.get_ticks()-tap_start_t
                dist=math.hypot(fx-tap_start[0],fy-tap_start[1]) if tap_start else 99
                if tap_start and dist<22 and dt<300:
                    tx,ty=tap_start
                    handled=False
                    for btn,action in [(btn_fit,lambda:vp.fit(objects,cx,cy,cw,ch)),
                                       (btn_zi, lambda:vp.zoom(1.3,cx+cw/2,cy+ch/2)),
                                       (btn_zo, lambda:vp.zoom(0.77,cx+cw/2,cy+ch/2))]:
                        if btn.collidepoint(tx,ty): action(); handled=True; break
                    if not handled and btn_back.collidepoint(tx,ty):
                        touch.remove(ev.finger_id); return 'back'
                    if not handled:
                        for k,r in layer_rects.items():
                            if pygame.Rect(r).collidepoint(tx,ty):
                                layer_vis[k]=not layer_vis[k]; handled=True; break
                    if not handled and in_canvas(tx,ty):
                        tap_obj=hit_test(tx,ty)
                tap_start=None
                touch.remove(ev.finger_id)
                if touch.count()<2: prev_span=None
                if touch.count()==0: prev_centroid=None

        # ── Render ─────────────────────────────────────────────────────────────
        screen.fill(BG)

        # Grid
        grid_sz=640
        x0w,y0w=vp.s2w(cx,cy); x1w,y1w=vp.s2w(cx+cw,cy+ch)
        gx0=math.floor(x0w/grid_sz)*grid_sz
        gy0=math.floor(y0w/grid_sz)*grid_sz
        for gx in range(int(gx0),int(x1w)+grid_sz,grid_sz):
            gsx,_=vp.w2s(gx,0)
            if cx<gsx<cx+cw:
                pygame.draw.line(screen,(18,32,75),(int(gsx),cy),(int(gsx),cy+ch))
                screen.blit(font_tiny.render(str(gx),True,(61,107,255)),(int(gsx)+2,cy+2))
        for gy in range(int(gy0),int(y1w)+grid_sz,grid_sz):
            _,gsy=vp.w2s(0,gy)
            if cy<gsy<cy+ch:
                pygame.draw.line(screen,(18,32,75),(cx,int(gsy)),(cx+cw,int(gsy)))
                screen.blit(font_tiny.render(str(gy),True,(61,107,255)),(cx+2,int(gsy)-12))

        # Objects
        buckets={k:[] for k in DRAW_ORDER}; buckets['start']=[]
        for obj in objects:
            if not is_visible(obj): continue
            t=obj.get('type','')
            if t=='block':
                (buckets['back'] if obj.get('perspective')=='back' else buckets['block']).append(obj)
            elif t=='spawn_point':     buckets['spawn'].append(obj)
            elif t=='moving_platform': buckets['platform'].append(obj)
            elif t in buckets:         buckets[t].append(obj)
        for k in DRAW_ORDER:
            for obj in buckets.get(k,[]): draw_object(screen,obj,vp,font_tiny)

        # Origin crosshair
        o0x,o0y=vp.w2s(0,0)
        if cx<o0x<cx+cw and cy<o0y<cy+ch:
            pygame.draw.line(screen,(200,180,50),(int(o0x)-12,int(o0y)),(int(o0x)+12,int(o0y)),1)
            pygame.draw.line(screen,(200,180,50),(int(o0x),int(o0y)-12),(int(o0x),int(o0y)+12),1)
        pygame.draw.rect(screen,BORDER,(cx,cy,cw,ch),1)

        # ── Sidebar / Drawer ────────────────────────────────────────────────────
        draw_panel(screen,(sx0,sy0,sw0,sh0),alpha=240)
        layer_rects.clear()

        if not mobile:
            # ── PC left sidebar ─────────────────────────────────────────────────
            tw,_=draw_text(screen,font_lg,'PIXEL',TEXT,sx0+10,sy0+8)
            draw_text(screen,font_lg,'ABYSS',ACCENT,sx0+10+tw,sy0+8)
            draw_text(screen,font_sm,'LEVEL VIEWER',MUTED,sx0+10,sy0+40)
            pygame.draw.line(screen,BORDER,(sx0,sy0+58),(sx0+sw0,sy0+58))

            draw_text(screen,font_sm,'FILE',ACCENT,sx0+10,sy0+64)
            nd=filename[:-5] if filename.endswith('.json') else filename
            while font_sm.size(nd+'…')[0]>sw0-20 and len(nd)>1: nd=nd[:-1]
            if len(nd)<len(filename[:-5] if filename.endswith('.json') else filename): nd+='…'
            draw_text(screen,font_sm,nd,TEXT,sx0+10,sy0+80)
            pygame.draw.line(screen,BORDER,(sx0,sy0+100),(sx0+sw0,sy0+100))

            draw_text(screen,font_sm,'LAYERS',ACCENT,sx0+10,sy0+106)
            draw_text(screen,font_tiny,'click row or 1-9',MUTED,sx0+sw0-106,sy0+110)

            ROW_H=28
            for i,(k,label,clr) in enumerate(LAYERS):
                ry=sy0+124+i*ROW_H
                vis=layer_vis[k]
                row_r=(sx0,ry,sw0,ROW_H-2)
                layer_rects[k]=row_r
                # Hover highlight
                if pygame.Rect(row_r).collidepoint(mx,my):
                    draw_rect_alpha(screen,ACCENT,row_r,30)
                # Toggle indicator stripe on left edge
                stripe_col=clr if vis else MUTED
                pygame.draw.rect(screen,stripe_col,(sx0,ry,4,ROW_H-2))
                # Swatch
                pygame.draw.rect(screen,clr if vis else MUTED,(sx0+10,ry+7,11,11))
                pygame.draw.rect(screen,BORDER,(sx0+10,ry+7,11,11),1)
                if not vis:
                    pygame.draw.line(screen,ACCENT2,(sx0+10,ry+7),(sx0+21,ry+18),2)
                # Key hint + label
                draw_text(screen,font_tiny,str(i+1),MUTED,sx0+26,ry+8)
                draw_text(screen,font_sm,label,TEXT if vis else MUTED,sx0+38,ry+6)
                # Count badge
                c=counts.get(k,0)
                if c: draw_text(screen,font_tiny,str(c),MUTED,sx0+sw0-28,ry+8)

            sep_y=sy0+124+len(LAYERS)*ROW_H+4
            pygame.draw.line(screen,BORDER,(sx0,sep_y),(sx0+sw0,sep_y))

            # Stats
            st_y=sep_y+8
            draw_text(screen,font_sm,'STATS',ACCENT,sx0+10,st_y); st_y+=18
            pal_str=','.join(PAL_NAMES.get(p,'?') for p in sorted(palettes)) or 'Default'
            for lbl,val in [('Objects',str(total)),('Palette',pal_str),('Zoom',f'{round(vp.scale*100)}%')]:
                draw_text(screen,font_sm,lbl,MUTED,sx0+10,st_y)
                draw_text(screen,font_sm,val,TEXT,sx0+sw0//2,st_y); st_y+=16
            if in_canvas(mx,my):
                wx,wy=vp.s2w(mx,my)
                draw_text(screen,font_tiny,f'x:{int(wx)}  y:{int(wy)}',MUTED,sx0+10,st_y)
            st_y+=15
            pygame.draw.line(screen,BORDER,(sx0,st_y+2),(sx0+sw0,st_y+2))
            hint_y=st_y+8
            for line in ['F fit   ESC back','Drag pan   Scroll zoom','1-9 toggle layers']:
                draw_text(screen,font_tiny,line,MUTED,sx0+8,hint_y); hint_y+=14

        else:
            # ── Mobile bottom drawer ──────────────────────────────────────────
            # Row 1: layers 1-5, Row 2: layers 6-9 (padded)
            LBTN_H=44; LBTN_W=(W-16)//5; GAP=4
            for i,(k,label,clr) in enumerate(LAYERS):
                col=i%5; row=i//5
                bx2=8+col*(LBTN_W+GAP)
                by2=sy0+8+row*(LBTN_H+GAP)
                vis=layer_vis[k]
                r=(bx2,by2,LBTN_W,LBTN_H)
                layer_rects[k]=r
                # Button bg
                draw_panel(screen,r,alpha=230,
                           colour=BTN_HOV if pygame.Rect(r).collidepoint(mx,my) else BTN_BG)
                # Border = layer colour when on, muted when off
                pygame.draw.rect(screen,clr if vis else MUTED,
                                 (int(r[0]),int(r[1]),int(r[2]),int(r[3])),2)
                # Dot indicator
                dot_x=bx2+9; dot_y=by2+LBTN_H//2
                pygame.draw.circle(screen,clr if vis else MUTED,(dot_x,dot_y),5)
                if not vis:
                    pygame.draw.line(screen,ACCENT2,(dot_x-4,dot_y-4),(dot_x+4,dot_y+4),2)
                # Short label + count
                short=label[:7]
                draw_text(screen,font_tiny,short,TEXT if vis else MUTED,bx2+18,by2+4)
                c=counts.get(k,0)
                if c: draw_text(screen,font_tiny,str(c),MUTED,bx2+18,by2+19)

            # Info strip
            info_y=sy0+8+2*(LBTN_H+GAP)+6
            pygame.draw.line(screen,BORDER,(0,info_y),(W,info_y))
            info_y+=5
            nd=filename[:-5] if filename.endswith('.json') else filename
            tw2,_=draw_text(screen,font_tiny,nd,ACCENT,8,info_y)
            draw_text(screen,font_tiny,f'  {total} objs  {round(vp.scale*100)}%  tap canvas for info',
                      MUTED,8+tw2,info_y)

        # ── Canvas buttons (always) ──────────────────────────────────────────
        draw_button(screen,font_sm,'FIT', btn_fit, bhov(btn_fit))
        draw_button(screen,font_sm,'Z+',  btn_zi,  bhov(btn_zi))
        draw_button(screen,font_sm,'Z-',  btn_zo,  bhov(btn_zo))
        draw_button(screen,font_sm,'◀BCK',btn_back,bhov(btn_back))

        # ── Tooltip ─────────────────────────────────────────────────────────
        if not dragging:
            tooltip_obj = (hit_test(mx,my) if in_canvas(mx,my) else None) if not mobile else tap_obj

        if tooltip_obj:
            obj=tooltip_obj
            lines=[('type',obj.get('type',''),ACCENT)]
            if obj.get('name'):       lines.append(('name',obj['name'],GOLD))
            if isinstance(obj.get('color'),str): lines.append(('color',obj['color'],TEXT))
            if obj.get('water_type'): lines.append(('water_type',obj['water_type'],TEXT))
            if obj.get('rise') is not None: lines.append(('rise',str(obj['rise']),TEXT))
            if obj.get('speed'):      lines.append(('speed',str(obj['speed']),TEXT))
            if obj.get('interval'):   lines.append(('interval',f"{obj['interval']}s lim:{obj.get('limit','')}",TEXT))
            if obj.get('entities'):   lines.append(('spawns',', '.join(f"{e[0]} {e[1]}" for e in obj['entities']),TEXT))
            lines.append(('pos',f"x:{obj.get('x',0)} y:{obj.get('y',0)}  {obj.get('width',64)}×{obj.get('height',64)}",MUTED))

            lh=15; pad=8
            tt_w=max(font_tiny.size(f'{k}: {v}')[0] for k,v,_ in lines)+pad*2+4
            tt_h=len(lines)*lh+pad*2
            if not mobile:
                tx=min(mx+14,W-tt_w-4); ty=min(my+14,H-tt_h-4)
            else:
                tx=max(4,(W-tt_w)//2); ty=max(4,sy0-tt_h-8)
            draw_panel(screen,(tx,ty,tt_w,tt_h),248)
            for i,(k,v,col) in enumerate(lines):
                kw=font_tiny.size(f'{k}: ')[0]
                draw_text(screen,font_tiny,f'{k}: ',MUTED,tx+pad,ty+pad+i*lh)
                draw_text(screen,font_tiny,v,col,tx+pad+kw,ty+pad+i*lh)

        pygame.display.flip()
        clock.tick(60)

# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen=pygame.display.set_mode((1280,800),pygame.RESIZABLE)
    pygame.display.set_caption('PIXEL ABYSS — Level Viewer')
    clock=pygame.time.Clock()

    def try_font(names,size):
        for n in names:
            try:
                f=pygame.font.SysFont(n,size)
                if f: return f
            except: pass
        return pygame.font.Font(None,size)

    mono=['couriernew','dejavusansmono','liberationmono','ubuntumono','monospace']
    fonts=(try_font(mono,28),try_font(mono,16),try_font(mono,14),try_font(mono,11))

    levels_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),'levels')

    if len(sys.argv)>1 and os.path.isfile(sys.argv[1]):
        result=run_viewer(screen,clock,fonts,sys.argv[1])
        if result=='quit': pygame.quit(); return

    while True:
        chosen=run_level_list(screen,clock,fonts,levels_dir)
        if chosen is None: break
        result=run_viewer(screen,clock,fonts,chosen)
        if result=='quit': break

    pygame.quit()

if __name__=='__main__':
    main()
